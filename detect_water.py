import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
leak_channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(leak_channel,GPIO.IN)
client = mqtt.Client()

leak_topic = "/home/brady/leak"
status_topic = "home/brady/status"
this_pi = "brady"
this_pi_password = "tom"

def on_connect(client,userdata,flags,rc):
    print ("connected with code "+str(rc))

def leak_update(channel) :
        if GPIO.input(channel):
            print("no water")
            client.publish(leak_topic, "dry", 1)
        else:
            print("water detected")
            client.publish(leak_topic, "wet", 1)

def initialize_states() :
    client.publish(status_topic, "online",1)
    leak_update(leak_channel)

client.username_pw_set(this_pi,this_pi_password)        
client.on_connect=on_connect
client.set_will(status_topic, payload = mk_payload("offline"))

client.connect("homeassistant.local", 1883,60)


GPIO.add_event_detect(leak_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(leak_channel, leak_update)

initialize_states()
client.loop_forever()
