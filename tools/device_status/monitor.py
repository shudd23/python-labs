from datetime import datetime
import os
import time
import logging
import requests
import socket
import fcntl
import struct
import re
import paho.mqtt.client as mqtt
from config import *

logging.basicConfig(level=logging.DEBUG)

HOSTNAME = socket.gethostname()
THE_TOPIC = HOSTNAME+"/#"
STATUC_TOPIC = HOSTNAME+"/status"
CMD_TOPIC = HOSTNAME+"/cmd"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode('utf8')
    logging.info(topic+" - "+message.replace("\n", " ") +
                 " ("+str(msg.qos)+","+str(msg.retain)+")")
    if topic == CMD_TOPIC and message == 'status':
        publish_status()


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result: "+mqtt.error_string(rc))
    # client.subscribe("$SYS/#")
    client.subscribe(THE_TOPIC)
    client.publish(STATUC_TOPIC, "Online", retain=True)
    publish_status()


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result: "+mqtt.error_string(rc))


def publish_status():
    ip = get_ip()
    uname = ' '.join(os.uname())
    client.publish(
        STATUC_TOPIC, "{} is running, ip is {} ({})".format(HOSTNAME, ip, uname))


def create_client():
    client = mqtt.Client(clean_session=True)
    # client.enable_logging()
    # client.on_log = on_log
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.will_set(STATUC_TOPIC, payload="Offline", retain=True)
    client.connect(MQTT_SERVER, port=MQTT_PORT, keepalive=60)
    return client


if __name__ == "__main__":
    client = create_client()
    logging.info("====================")
    logging.info("OrangePi online")
    client.loop_forever()