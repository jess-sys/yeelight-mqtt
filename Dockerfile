FROM python:3

ENV MQTT_BROKER=172.30.42.60
ENV MQTT_PORT=1883
ENV MQTT_HA_DISCOVERY_TOPIC_BASE=homeassistant
ENV LIGHT_IP=172.30.42.203

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]