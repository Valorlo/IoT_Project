import random
import time
import json
from paho.mqtt import client as mqtt_client


broker = '140.127.208.60'
port = 1883
GPS_topic = "/AILAB/DRONE/GPS"
STAT_topic = "/AILAB/DRONE/STAT"
pub_DST = "/AILAB/DRONE/DST"
pub_GO = "/AILAB/DRONE/GO"
pub_RTL = "/AILAB/DRONE/RTL"
# generate client ID with pub prefix randomly

client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'DKPK49AE9ZS9ZX5577'
# password = 'DKPK49AE9ZS9ZX5577'

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

def drone_init(client: mqtt_client):
    msg = ""
    result = client.publish(pub_DST, json.dumps(msg))
    msg = "0"
    result = client.publish(pub_RTL, json.dumps(msg))
    msg = "0"
    result = client.publish(pub_GO, json.dumps(msg))
    



def GPS_subscribe(client: mqtt_client):
    # print("subscribe")
    GPS_reply = ""
    def on_message(client, userdata, msg):
        global GPS_reply
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        GPS_reply = msg.payload.decode()
        # GPS_reply = switch_control['value'][0]
        print(GPS_reply)

    # print("out",GPS_reply)
    client.subscribe(GPS_topic)
    client.on_message = on_message

def STAT_subscribe(client: mqtt_client):
    # print("subscribe")
    STAT_reply = ""
    def on_message(client, userdata, msg):
        global STAT_reply
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        STAT_reply = msg.payload.decode()
        # GPS_reply = switch_control['value'][0]
        print(STAT_reply)

    # print("out",GPS_reply)
    client.subscribe(STAT_topic)
    client.on_message = on_message

def publish_DST(client,where):
    msg = where
    result = client.publish(pub_DST, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_DST}`")
    else:
        print(f"Failed to send message to topic {pub_DST}")

    # time.sleep(30)
def publish_RTL(client):
    msg ="1"
    result = client.publish(pub_RTL, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_RTL}`")
    else:
        print(f"Failed to send message to topic {pub_RTL}")

def publish_GO(client):
    msg ="1"
    result = client.publish(pub_GO, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_GO}`")
    else:
        print(f"Failed to send message to topic {pub_GO}")

def run():
    client = connect_mqtt()
    publish_RTL(client)
    while True:
        GPS_subscribe(client)
        STAT_subscribe(client)
        time.sleep(3)
        client.loop()

if __name__ == '__main__':
    client = connect_mqtt()
    publish_RTL(client)
    GPS_subscribe(client)