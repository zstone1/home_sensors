#!/bin/bash

pip3 install paho-mqtt
pip3 install Adafruit-DHT

sudo cp sense.service /etc/systemd/system/sense.service
sudo systemctl enable sense.service
