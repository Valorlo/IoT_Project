import random
import time
import json
from paho.mqtt import client as mqtt_client

client_id = f'python-mqtt-{random.randint(0, 100)}'

class broker:
    def __init__(self) : 
        self.broker = '140.127.208.60'
        self.port = 1883
        self.GPS_topic = "AILAB/IOT/DRONE/GPS"
        self.STAT_topic = "AILAB/IOT/DRONE/STATE"
        self.HIGH_topic = "AILAB/IOT/DRONE/HIGH"
        self.pub_DST = "AILAB/IOT/SERVER/DST"
        self.pub_GO = "AILAB/IOT/SERVER/GO"
        self.pub_RTL = "AILAB/IOT/SERVER/RTL"

        def connect_mqtt() -> mqtt_client:
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    print("Connected to MQTT Broker!")
                else:
                    
                    print("Failed to connect, return code %d\n", rc)

            client = mqtt_client.Client(client_id)
            # client.username_pw_set(username, password)
            client.on_connect = on_connect
            client.connect(self.broker, self.port)
            return client

        self.client = connect_mqtt()
        

        self.client = mqtt_client.Client(client_id)
        # client.username_pw_set(username, password)
        self.client.on_connect = on_connect
        self.client.connect(broker, port)
        return self.client

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

# def run():
#     # client = connect_mqtt()
    

if __name__ == '__main__':
    PUB = broker()
    PUB.GPS_subscribe()
    PUB.STAT_subscribe()