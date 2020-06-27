import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from gpiozero import MotionSensor

import Adafruit_DHT
import json
pir_channel = 4
leak_a_channel = 14
leak_b_channel = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(leak_a_channel,GPIO.IN)
GPIO.setup(leak_b_channel,GPIO.IN)
GPIO.setup(pir_channel,GPIO.IN)

client = mqtt.Client()
dht_sensor = Adafruit_DHT.DHT22
dht_pin = 18

this_pi = "brady"

leak_a_topic = f"/home/{this_pi}/leak/A"
leak_b_topic = f"/home/{this_pi}/leak/B"
pir_topic = f"/home/{this_pi}/pir"
climate_topic = f"/home/{this_pi}/climate"
status_topic = f"/home/{this_pi}/status"
reinitialize = "/reinitialize"
this_pi_password = "tom"

def leak_update(topic,channel) :
        if GPIO.input(channel):
            print("no water")
            client.publish(topic, "dry", 1)
        else:
            print("water detected")
            client.publish(topic, "wet", 1)
def leak_a_update(channel) : 
    leak_update(leak_a_topic,channel)
def leak_b_update(channel) : 
    leak_update(leak_b_topic,channel)

def pir_update(channel): 
   if GPIO.input(channel):
       print(f"pir turned on")
       client.publish(pir_topic, "detected",1)
   else:
       print(f"pir turned off")

def climate_update():
    h,t = Adafruit_DHT.read(dht_sensor, dht_pin)
    if h is not None and t is not None:
      sensor_data = { "temperature": round(t,2), "humidity": round(h,2) }
      j = json.dumps(sensor_data)
      print(f"json formatted:: {json.dumps(sensor_data)}")
      client.publish(climate_topic, j, 1)
    else: 
      print(f"sensor read failure")

def initialize_states() :
    print("connected to broker")
    client.publish(status_topic, "online",1)
    leak_a_update(leak_a_channel)
    leak_b_update(leak_b_channel)
    climate_update()

def receive_msg(client, userdata, msg) : 
    print(f"received a message on {msg.topic}")
    switcher = {
            reinitialize: initialize_states
    }
    switcher.get(msg.topic, lambda: ())()

def on_connect(client,userdata,flags,rc):
    initialize_states() 
    res = client.subscribe(reinitialize, qos=1)
    print(f"sub result: {res}")

def on_disconnect(client, ud, rc):
    print(f"Disconnected with error: {rc}")

client.username_pw_set(this_pi,this_pi_password)        
client.on_connect=on_connect
client.on_disconnect=on_disconnect
client.will_set(status_topic, payload = "offline")
client.on_message = receive_msg

client.connect("10.0.0.9", 1883,2)

GPIO.add_event_detect(leak_a_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(leak_a_channel, leak_a_update)

GPIO.add_event_detect(leak_b_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(leak_b_channel, leak_b_update)

GPIO.add_event_detect(pir_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(pir_channel, pir_update)

client.loop_start()

while True:
    time.sleep(6)
    climate_update()







