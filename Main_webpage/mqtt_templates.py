# QTT Broker settings
# Author : buikh

import paho.mqtt.client as client
import paho.mqtt.publish as publish
import json
import time
import os

# Multithreading and processing
import threading
import multiprocessing
import queue

# Logging Call
import logging
import subprocess
import random

# Setting Logging level by MQTT
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT Broker settings
broker = 'mqtt://192.168.128.105'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'


#### SETTING UP PUBLISHING TO A SPECIFY CLIENT ####
#### CLIENT IS RULED BY THE CLIENT ID ####
#### This is just interface between client and the MQTT Broker cannnot work client with client 

def connect_mqtt_pub():
    "This function connects to the MQTT broker and sets up the client."
    "This function only send a connection to one client only"

    def on_connect(client, userdata, flags, rc):
        logging.debug(f"Connected with result code {rc}")

        if rc == 0:
            logging.info("Connected to MQTT Broker!")
            logging.info(f"The client the{client}")
            logging.info(f"Client ID: {client_id}")
            logging.info(f"MQTT Code status: {rc}")
            logging.info(f"Broker TCP Port: {port}")
            logging.info(f"Broker ID: {broker}")
        else:
            logging.error("Failed to connect, return code %d\n", rc)
        
    client = client.Client(client_id)
    # client.username_pw_set("username", "your_username")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg):
    "This function publishes a message to a topic."

    msg_count = 0
    logging.info(f"Message sent as '{msg_count}'")

    while True:
        time.sleep(5)  # Sleep for 5 seconds for the setting up time
        msg_count = 0
        ##### Parsing the received data here #####

        # msg = ......

        result = client.publish(topic, msg)
        status = result[0]

        if status == 0:
            logging.info(f"Sent '{msg}' to topic '{topic}'")
        else:
            logging.error(f"Failed to send message to topic {topic}")

        msg_count += 1
        logging.info(f"Message sent as '{msg_count} times")

def run_mqtt_publisher():
    "This function runs the MQTT publisher."
    " Parsing Client into client variable to run both MQTT Publisher and Subscriber at the same time"

    client = connect_mqtt_pub()
    topic = "test/topic"
    msg = "Hello, MQTT!"

    publish(client, topic, msg)

#### SETTING UP SUBCRIBING TO BROKER ####
#### This is just interface between client and the MQTT Broker cannnot work client with client 

def connect_mqtt_sub() -> mqtt_client:
    "This function connects to the MQTT broker and sets up the client."
    "This function only send a connection to one client only"

    def on_connect(client, userdata, flags, rc):
        logging.debug(f"Connected with result code {rc}")

        if rc == 0:
            logging.info("Connected to MQTT Broker!")
            logging.info(f"The client the{client}")
            logging.info(f"Client ID: {client_id}")
            logging.info(f"MQTT Code status: {rc}")
            logging.info(f"Broker TCP Port: {port}")
            logging.info(f"Broker ID: {broker}")
        else:
            logging.error("Failed to connect, return code %d\n", rc)
        
    client = client.Client(client_id)
    # client.username_pw_set("username", "your_username")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client,userdata_topic, msg):
    "This function subscribes to a topic and processes the messages received."

    def on_message(client, userdata_topic, msg):
        logging.info(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

        # Process the message and the received message
        msg_topic = msg.topic
        msg = msg.payload.decode()
        json_data = json.loads(msg)
    
    client.on_message = on_message
    client.loop_start()

def run_mqtt_subcription():
    
    "This function runs the MQTT subscriber."
    " Parsing Client into client variable to run both MQTT Publisher and Subscriber at the same time"

    client = connect_mqtt_sub()
    # client = 
    # topic = "test/topic" # Change this to the topic you want to subscribe to
    # msg = "Hello, MQTT!"
    subcribe(client, topic, msg)

if __name__ == "__main__":
    run_mqtt_subcription()

