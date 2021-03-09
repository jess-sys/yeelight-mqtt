# yeelight-mqtt

Integrate a Yeelight lamp (including the Screenbar YLTD001-003) in HomeAssistant using MQTT.

## Getting started

To use this project, you can set it up manually, or use the Docker image.

Some environement variables can be used:
* MQTT_BROKER (**required**) : the IP or Hostname of your MQTT Broker
* MQTT_PORT (optional) : the port of your MQTT Broker
* MQTT_HA_DISCOVERY_TOPIC_BASE (optional) : the MQTT prefix, defaults to `homeassistant`
* LIGHT_IP (**required**) : the IP of the light you want to control

## Docker usage

Available as a Docker Hub Package (https://hub.docker.com/repository/docker/jesssys/yeelight-mqtt).²

Edit the variables in the `docker-compose.yml` file and just run `docker-compose up`

## Credits

Author : Jessy SOBREIRO

Thanks to @skorokithakis (https://github.com/skorokithakis/python-yeelight)