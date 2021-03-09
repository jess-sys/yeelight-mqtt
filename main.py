import os, uuid, json, sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from timeloop import Timeloop
from datetime import timedelta

sys.path.append('./yeelight')
from yeelight import Bulb

tl = Timeloop()

LIGHT_IP = os.environ.get('LIGHT_IP')
bulb = Bulb(LIGHT_IP)

AVAILABILITY_PING_DELAY = os.environ.get('AVAILABILITY_PING_DELAY') or 120

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_PORT = os.environ.get('MQTT_PORT') or 1883
MQTT_HA_DISCOVERY_TOPIC_BASE = os.environ.get('MQTT_HA_DISCOVERY_TOPIC') or 'homeassistant'
MQTT_HA_DISCOVERY_TOPIC_BASE = MQTT_HA_DISCOVERY_TOPIC_BASE + "/light"

guid = {
    "UUID1": "",
    "UUID2": ""
}


def check_gen_uuid():
    UUIDs = {
        "UUID1": uuid.uuid1().hex[0:12],
        "UUID2": uuid.uuid4().hex[0:12]
    }

    for el in ["UUID1", "UUID2"]:
        f = open(el, "r+")
        content = f.readline()
        guid[el] = content
        if len(content) < 10:
            f.write(UUIDs[el])
        f.close()


@tl.job(interval=timedelta(seconds=AVAILABILITY_PING_DELAY))
def publish_availability():
    print("Sending availability...")
    publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID1"] + "/availability", "online", hostname=MQTT_BROKER)
    publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID2"] + "/availability", "online", hostname=MQTT_BROKER)


def on_connect(client, userdata, flags, rc):
    print("Connected to " + MQTT_BROKER)
    print("Subscribing to : " + MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID1"] + "/command")
    client.subscribe(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID1"] + "/command")
    print("Subscribing to : " + MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID2"] + "/command")
    client.subscribe(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID2"] + "/command")
    setup()
    tl.start(block=False)


def handle_yeelight(type, payload):
    payload = json.loads(payload)
    if type == "back":
        if "state" in payload:
            bulb.bg_turn_on() if payload['state'] == "ON" else bulb.bg_turn_off()
        if "color" in payload:
            bulb.bg_set_rgb(payload["color"]['r'], payload["color"]['g'], payload["color"]['b'])
        if "brightness" in payload:
            bulb.bg_set_brightness(payload['brightness'])
    else:
        if "state" in payload:
            bulb.turn_on() if payload['state'] == "ON" else bulb.turn_off()
        if "color_temp" in payload:
            bulb.set_color_temp(payload['color_temp'])
        if "brightness" in payload:
            bulb.set_brightness(payload['brightness'])


def on_message(client, userdata, msg):
    print(msg.topic + " - " + str(msg.payload))
    if "command" in msg.topic and guid["UUID1"] in msg.topic:
        handle_yeelight("front", msg.payload)
        publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID1"] + "/state", msg.payload,
                       hostname=MQTT_BROKER)
    if "command" in msg.topic and guid["UUID2"] in msg.topic:
        handle_yeelight("back", msg.payload)
        publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID2"] + "/state", msg.payload,
                       hostname=MQTT_BROKER)


def construct_light_discovery(uuid, is_bar):
    name_suffix = "Back light" if is_bar else "Front light"
    return json.dumps({
        "~": MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + uuid,
        "unique_id": uuid,
        "state_topic": "~/state",
        "schema": "json",
        "device": {
            "manufacturer": "Xiaomi",
            "model": "YeeLight Screenbar",
            "identifiers": uuid,
            "name": "YeeLight Screenbar",
            "sw_version": "1.337",
        },
        "effect": is_bar,
        "rgb": is_bar,
        "hs": is_bar,
        "xy": is_bar,
        "brightness": True,
        "brightness_scale": 100,
        "max_mireds": 6500,
        "min_mireds": 2700,
        "color_temp": not is_bar,
        "availability_topic": "~/availability",
        "command_topic": "~/command",
        "name": "YeeLight ScreenBar - " + name_suffix
    })


def setup():
    publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID1"] + "/config",
                   construct_light_discovery(guid["UUID1"], False), hostname=MQTT_BROKER, retain=True)
    publish.single(MQTT_HA_DISCOVERY_TOPIC_BASE + "/" + guid["UUID2"] + "/config",
                   construct_light_discovery(guid["UUID2"], True), hostname=MQTT_BROKER, retain=True)


check_gen_uuid()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_forever()
