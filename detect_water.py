import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
leak_channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(leak_channel,GPIO.IN)
client = mqtt.Client()

this_pi = "brady"

leak_topic = f"/home/{this_pi}/leak"
status_topic = f"/home/{this_pi}/status"
reinitialize = "/reinitialize"
this_pi_password = "tom"

def leak_update(channel) :
        if GPIO.input(channel):
            print("no water")
            client.publish(leak_topic, "dry", 1)
        else:
            print("water detected")
            client.publish(leak_topic, "wet", 1)

def initialize_states() :
    print("connected to broker")
    client.publish(status_topic, "online",1)
    leak_update(leak_channel)

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



client.username_pw_set(this_pi,this_pi_password)        
client.on_connect=on_connect
client.will_set(status_topic, payload = "offline")
client.on_message = receive_msg

client.connect("homeassistant.local", 1883,2)


GPIO.add_event_detect(leak_channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(leak_channel, leak_update)

client.loop_forever()
