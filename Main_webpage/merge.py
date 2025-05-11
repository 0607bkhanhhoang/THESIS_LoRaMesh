# Author: Bui Khanh Hoang

from collections import deque
import paho.mqtt.client as mqtt
import logging
import threading
import time
import json

import subprocess
from datetime import datetime
import os
import sys

# ===== Logging Configuration =====
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ===== Configuration =====
BROKER_IP = "192.168.143.105"
NODE_IDS = [f"node_{i}" for i in range(0, 5)]
DATA_TYPES = ["oxygen", "pH", "turbidity", "light", "air", "opto", "lat", "long"]

# ===== Initialize Nested Data Structure For visualize =====
node_data = {
    node_id: {
        data_type: deque([0] * 10, maxlen=10000) for data_type in DATA_TYPES
    }
    for node_id in NODE_IDS
}

# ======= Debug Print Function =======
def print_structure(data):
    for node_id, sensors in data.items():
        logging.info(f"{node_id}:")
        for sensor_type, dq in sensors.items():
            logging.info(f"  {sensor_type}: {list(dq)}")
    max_size = max(dq.maxlen for node in data.values() for dq in node.values())
    print("[INFO] Max size of deque:", max_size)

# ======= Json Parsing Function =======

def capture_mqtt_to_log(broker_ip="192.168.107.105", topic="/topic/node_1", log_file="node_1_log.txt"):
    """
    Capturing all MQTT data and save to log file.
    This log file will be used to parse the data later. By parsing the log data, we will save them into json file.
    """
    try:
        # Run mosquitto_sub as subprocess
        process = subprocess.Popen(["mosquitto_sub", "-h", broker_ip, "-t", topic],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        print(f"[INFO] Subscribed to {topic} at {broker_ip}. Logging to {log_file}...")

        with open(log_file, "a") as f:
            for line in process.stdout:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_line = f"[{timestamp}] {line}"
                print(log_line.strip())
                f.write(log_line)

    except FileNotFoundError:
        print("[ERROR] mosquitto_sub not found")
    except Exception as e:
        print(f"[ERROR] {e}")

# ======= Capture MQTT to Nested Data Structure =======
def parse_all_node_messages(topic, payload):
    """
    Parse the incoming MQTT message and update the nested data structure.
    """
    try:
        # Extract node ID from topic
        node_id = topic.split("/")[-1]

        # Check if node_id is valid
        if node_id not in NODE_IDS:
            logging.warning(f"Invalid node ID: {node_id}")
            return

        # Parse JSON payload
        parsed_data = json.loads(payload.decode('utf-8'))

        # Update the deque for each data type
        for data_type in DATA_TYPES:
            value = parsed_data.get(data_type, 0)
            node_data[node_id][data_type].append(value)

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
    except Exception as e:
        logging.error(f"Error parsing message: {e}")

# ======= Thread for capturing all nodes data and save into txt file =======
# Read last line of each log file 
def read_last_line(filepath):
    with open(filepath, 'rb') as f:
        f.seek(-2, 2)
        while f.read(1) != b'\n':
            f.seek(-2, 1)
        return f.readline().decode().strip()
    
def capture_all_nodes_data():

    capture_mqtt_to_log(broker_ip=BROKER_IP, topic="/topic/node_1", log_file="node_1.log")
    last_line = read_last_line("node_1.log")
    json_data_1 = json.loads(last_line)
    logging.info(f"Last line from node_1.log: {json_data_1}")
    print(json_data_1)

# Read last line of each log file 
def read_last_line(filepath):
    with open(filepath, 'rb') as f:
        f.seek(-2, 2)
        while f.read(1) != b'\n':
            f.seek(-2, 1)
        return f.readline().decode().strip()

# ======= MQTT Callback Functions =======
# =======================================

def collect_mqtt_messages_as_dict(topic, broker="localhost", port=1883, max_messages=40, use_timestamp=False):
    messages = {}
    done = {"count": 0}

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())

            # Key for each message: sequential or timestamp
            if use_timestamp:
                import datetime
                key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                key = f"msg_{done['count']}"

            messages[key] = data
            done["count"] += 1

            print(f"[{done['count']}/{max_messages}] ✅ {key}: {data}")

            if done["count"] >= max_messages:
                client.disconnect()

        except Exception as e:
            print("Error parsing message:", e)

    # Set up MQTT
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.subscribe(topic)

    logging.info(f"📡 Subscribed to '{topic}'... collecting {max_messages} messages")
    client.loop_forever()

    return messages

# ======= Function for parsing into nested list =======

def save_all_nodes_data_to_json(topic, node_data, data_recorded):
    """
    Save all nodes data to a JSON file and turn them into a nested list.
    """
    data_recorded =collect_mqtt_json_messages(topic, broker=BROKER_IP, max_messages=20)


# ======= Main Execution =======
if __name__ == "__main__":
    
    data_test = collect_mqtt_messages_as_dict("#", broker=BROKER_IP, max_messages=10)
    logging.info("Captured")
    print(data_test)

    # with open('static/data/node_1.json', 'r') as f:
    #     target_data = json.load(f)

    # for message in data_test:
    #     if 'oxygen' in message:  # Check if 'oxygen' key is in the current message
    #         data_test['oxygen'].append(message['oxygen'])  # Append the oxygen value to the list
    #         print("Updated Oxygen")  
        

    # with open('static/data/node_1.json', 'w') as f:
    #     json.dump(target_data, f, indent=2)  
    for id in range(1,5):
        target_data = {
            "oxygen": [],
            "pH": [],
            "turbidity": [],
            "light": [],
            "air": [],
            "opto_1": [],
            "opto_2": []
        }

        # Loop through messages in raw data
        for msg in data_test.values():
            for key in target_data.keys():
                if key in msg:
                    target_data[key].append(msg[key])

        # Write the parsed result to the target file
        with open(f'static/data/node_{id}.json', 'w') as f:
            json.dump(target_data, f, indent=2)
        
