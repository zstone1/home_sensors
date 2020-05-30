import RPi.GPIO as GPIO
from threading import Thread
import time
import paho.mqtt.client as mqtt
leak_channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(leak_channel,GPIO.IN)
client = mqtt.Client()

leak_topic = "/brady/leak"
ping_topic = "/brady/ping"

def on_connect(client,userdata,flags,rc):
    print ("connected with code "+str(rc))

def leak_update(channel) :
        if GPIO.input(channel):
            print("no water")
            client.publish(leak_topic,"dry", 0)
        else:
            print("water detected")
            client.publish(leak_topic,"wet", 0)

def send_ping():
  print("pinging:" + time.ctime())
  client.publish(ping_topic,"alive",0)
  time.sleep(30)
  send_ping()

client.username_pw_set("brady","tom")        
client.on_connect=on_connect

client.connect("homeassistant.local", 1883,60)



GPIO.add_event_detect(leak_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(leak_channel, leak_update)
t = Thread(target=send_ping)
t.start()
leak_update(leak_channel)
client.loop_forever()
