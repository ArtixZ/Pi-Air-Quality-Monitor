# Pi-Air-Quality-Monitor


## Hardware Prerequisite

- Raspberry pi
- SDS011 air quality monitor

## Getting started

- pip install python-aqi pyserial psutil paho-mqtt
- Add `channelID` and `apiKey` into .config.txt file. (Register for free at https://thingspeak.com)

- run `python airQuality.py`



## Features
- Read pm2.5, pm10. Converts them into AQI index.
- Upload data to IoT platform (e.g. https://thingspeak.com).
