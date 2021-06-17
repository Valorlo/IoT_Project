import random
import time
import json
from paho.mqtt import client as mqtt_client


broker = '140.127.208.184'
port = 1883
topic = "/AILAB/IOT/DRONE/#"
pub_topic = "/AILAB/IOT/DRONE/DST"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# client2_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'DKPK49AE9ZS9ZX5577'
# password = 'DKPK49AE9ZS9ZX5577'
GPSx=""
GPSy=""
RTL=""
GO=""
switch_control=""

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client




def subscribe(client: mqtt_client):
    # print("subscribe")
    def on_message(client, userdata, msg):
        # global switch_control
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        switch_control = json.loads(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message
    time.sleep(10)


def destination_publish(client):
    GPSx=""
    GPSy=""
    global switch_control
    # print("publish")
    # print("switch_control: ",switch_control)
    if GPSx!= "" and GPSy!= "":
        msg = [{'GPS':"("+GPSx+","+GPSy+")"}]
        result = client.publish(pub_topic, json.dumps(msg))
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{pub_topic}`")
        else:
            print(f"Failed to send message to topic {pub_topic}")
        time.sleep(30)


def RTL_publish(client):
    RTL =""
    # print("publish")
    # print("switch_control: ",switch_control)
    if RTL!= "":
        msg = [{'RTL':str(RTL)}]
        result = client.publish(pub_topic, json.dumps(msg))
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{pub_topic}`")
        else:
            print(f"Failed to send message to topic {pub_topic}")
        time.sleep(30)


def GO_publish(client):
    GO =""
    # print("publish")
    # print("switch_control: ",switch_control)
    if GO!= "":
        msg = [{'RTL':str(GO)}]
        result = client.publish(pub_topic, json.dumps(msg))
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{pub_topic}`")
        else:
            print(f"Failed to send message to topic {pub_topic}")
        time.sleep(30)

def run():
    client = connect_mqtt()
    while True:
        subscribe(client)
        destination_publish(client)
        client.loop()

if __name__ == '__main__':
    run()