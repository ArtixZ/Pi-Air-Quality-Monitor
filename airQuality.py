import time
from datetime import datetime
import os
import paho.mqtt.publish as publish
import psutil
import aqi
import configparser

from sds011 import *

# pip install python-aqi pyserial psutil
# sudo pip install paho-mqtt

parser = configparser.ConfigParser()
parser.read(".config.txt")

channelID = parser.get("MQTT", "channelID")
topic = "channels/" + channelID + "/publish"
mqttHost = parser.get("MQTT", "mqttHost")
clientID = parser.get("MQTT", "client_id")
username = parser.get("MQTT", "username")
pswd = parser.get("MQTT", "password")


# Conventional TCP socket on port 1883.
# This connection method is the simplest and requires the least system resources.
tTransport = "websockets"
tPort = 80
tTLS = None


# tPayload = "field1=" + str(pmt_2_5) + "&field2=" + str(aqi_2_5) + \
#     "&field3=" + str(pmt_10) + "&field4=" + str(aqi_10)

sensor = SDS011("/dev/ttyUSB0")


def get_data(n=3):
    sensor.sleep(sleep=False)
    pmt_2_5 = 0
    pmt_10 = 0
    time.sleep(10)
    for i in range(n):
        x = sensor.query()
        pmt_2_5 = pmt_2_5 + x[0]
        pmt_10 = pmt_10 + x[1]
        time.sleep(2)
    pmt_2_5 = round(pmt_2_5 / n, 1)
    pmt_10 = round(pmt_10 / n, 1)
    sensor.sleep(sleep=True)
    time.sleep(2)
    return pmt_2_5, pmt_10


def conv_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
    return aqi_2_5, aqi_10


def save_log():
    cwd = os.getcwd()

    with open(cwd + "/air_quality.csv", "a") as log:
        pmt_2_5, pmt_10 = get_data()
        aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
        dt = datetime.now()
        log.write("{},{},{},{},{}\n".format(dt, pmt_2_5, aqi_2_5, pmt_10, aqi_10))
    log.close()


while True:
    pmt_2_5, pmt_10 = get_data()
    aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
    tPayload = (
        "field1="
        + str(pmt_2_5)
        + "&field2="
        + str(aqi_2_5)
        + "&field3="
        + str(pmt_10)
        + "&field4="
        + str(aqi_10)
    )
    try:
        publish.single(
            topic,
            payload=tPayload,
            hostname=mqttHost,
            port=tPort,
            tls=tTLS,
            transport=tTransport,
            client_id=clientID,
            auth={
                "username": username,
                "password": pswd,
            },
        )
        save_log()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("[INFO] Failure in sending data")
    time.sleep(60)
