#!/usr/bin/python3
import config   #copy config-example.py to config.py and set values
import sys
import time
import random
import uuid
import paho.mqtt.client as mqtt

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + uuid

def main(args):
    if len(args) <= 1:
        print ("Specify unit simulation file to use")
        exit()

    count = 0
    config = ""
    simulation = "stepwise"

    #Figure out what arguments were specified
    for arg in args:
        if count == 1:
            config = arg
            topic = arg
        if count == 2:
            if arg == "random":
                simulation = "random"
        if count == 3:
            topic = arg
        count += 1

    #Figure out what config file to use
    file1 = open(config + '.txt', 'r')
    print ("Using Config:    " + config + '.txt')
    print ("MQTT Client ID:  " + mqtt_clientid)
    print ("Publish Topic:   " + topic)
    print ("Simulation Type: " + simulation)
    print()

    #Connect to Broker
    mqtt_client = mqtt.Client(mqtt_clientid)
    mqtt_client.connect(mqtt_broker)

    #Call selected simulation function with needed values from config
    if simulation == "random":
        Lines = file1.readlines()
        high_num = 0.0
        low_num = 10000000000.0
        for line in Lines:
            currNum = float(line.strip())
            if currNum > high_num:
                high_num = currNum
            if currNum < low_num:
                low_num = currNum
        simulate_random(low_num, high_num, topic, mqtt_client)
    else:
        simulate_stepwise(file1.readlines(), topic, mqtt_client)

def simulate_stepwise(lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            for line in lines:
                count += 1
                mqtt_publish(line.strip(), topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_random(low, high, topic, mqtt_client):
    try:
        while True:
            for x in range(10):
                new_num = round(random.uniform(low, high), 1)
                mqtt_publish(new_num, topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def mqtt_publish(value, topic, mqtt_client):
    print (topic.capitalize() + " Value: " + str(value))
    mqtt_client.publish(topic, value)

if __name__ == "__main__":
    print()
    print ("CESMI IIOT Simulator")
    print ("=============================")
    print ("")
    main(sys.argv)