#!/usr/bin/python3
import config   #copy config-example.py to config.py and set values
import sys
import time
import random
import uuid
import paho.mqtt.client as mqtt
import random

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
    num_simutank = 1
    #Figure out what arguments were specified
    for arg in args:
        if count == 1:
            config = arg
            topic = arg
        elif count == 2:
            simulation = arg
            #simulation=arg
        elif count == 3:
            topic = arg
        elif count == 4:
            num_simutank = int(arg)
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
    Lines = file1.readlines()
    if simulation == "random":
        high_num = 0.0
        low_num = 10000000000.0
        count_tanks=0
        for line in Lines:
            count+=1
            currNum = float(line.strip())
            if currNum > high_num:
                high_num = currNum
            if currNum < low_num:
                low_num = currNum
        simulate_random(low_num, high_num, topic, mqtt_client)
    elif simulation == "stepwise":
        simulate_stepwise(Lines, topic, mqtt_client)

    randomtanks=sorted(random.sample(range(0,len(Lines)), num_simutank))
    Lines = [float(ele.strip()) for ele in Lines]
    if simulation == "randomleak":
        simulate_randomleak(randomtanks, num_simutank, Lines, topic, mqtt_client)
    elif simulation == "randomfill":
        simulate_randomfill(randomtanks, num_simutank, Lines, topic, mqtt_client)
    elif simulation == "fillwithhole":
        simulate_fillwithhole(randomtanks, num_simutank, Lines, topic, mqtt_client)
    elif simulation == "randomfillandleak":
        count_leak=random.randint(1, len(Lines))
        count_fill=random.randint(1, len(Lines))
        randomleaktanks=sorted(random.sample(range(0,len(Lines)), count_leak))
        randomfilltanks=sorted(random.sample(range(0,len(Lines)), count_fill))
        simulate_randomfillandleak(randomleaktanks, count_leak, randomfilltanks, count_fill, Lines, topic, mqtt_client)
    elif simulation == "producewithleak":
        randomleaktanks=sorted(random.sample(range(1,len(Lines)-1), num_simutank))
        simulate_producewithleak(randomleaktanks, num_simutank, Lines, topic, mqtt_client)
    elif simulation == "producewithfillandleak":
        count_leak=random.randint(1, len(Lines)-2)
        count_fill=random.randint(1, len(Lines)-2)
        randomleaktanks=sorted(random.sample(range(1,len(Lines)), count_leak))
        randomfilltanks=sorted(random.sample(range(1,len(Lines)), count_fill))
        simulate_producewithfillandleak(randomleaktanks, count_leak, randomfilltanks, count_fill, Lines, topic, mqtt_client)
    elif simulation == "produce":
        simulate_produce(Lines, topic, mqtt_client)
    elif simulation == "producewithfill":
        randomfilltanks=sorted(random.sample(range(1,len(Lines)-1), num_simutank))
        simulate_producewithfill(randomfilltanks, num_simutank, Lines, topic, mqtt_client)

def simulate_produce(lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            lines[0] += 2
            while count < (len(lines)-1):
                if lines[count] == 0:
                    while count < (len(lines)-1):
                        mqtt_publish(str(lines[count]), topic, mqtt_client)
                        time.sleep(1)
                        count += 1
                else:              
                    lines[count] -= 1
                    lines[count+1] += 1
                    mqtt_publish(str(lines[count]), topic, mqtt_client)
                    time.sleep(1)
                    count += 1
            mqtt_publish(str(lines[count]), topic, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_producewithleak(randomtanks, count_leak, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            lines[0] += 2
            while count < (len(lines)-1):
                if index_tank < count_leak and count == randomtanks[index_tank]:
                    lines[count] -= 1.0
                    lines[count] = max(lines[count], 0)
                    index_tank += 1
                if lines[count] == 0.0:
                    while count < (len(lines)-1):
                        mqtt_publish(str(lines[count]), topic, mqtt_client)
                        time.sleep(1)
                        count += 1
                else:              
                    lines[count] -= 1.0
                    lines[count+1] += 1.0
                    mqtt_publish(str(lines[count]), topic, mqtt_client)
                    time.sleep(1)
                    count += 1
            mqtt_publish(str(lines[count]), topic, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_producewithfill(randomtanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            lines[0] += 2
            while count < (len(lines)-1):
                if index_tank < count_fill and count == randomtanks[index_tank]:
                    lines[count] += 1.0
                    lines[count] = min(lines[count], 10)
                    index_tank += 1
                if lines[count] == 0.0:
                    while count < (len(lines)-1):
                        mqtt_publish(str(lines[count]), topic, mqtt_client)
                        time.sleep(1)
                        count += 1
                else:              
                    lines[count] -= 1.0
                    lines[count+1] += 1.0
                    mqtt_publish(str(lines[count]), topic, mqtt_client)
                    time.sleep(1)
                    count += 1
            mqtt_publish(str(lines[count]), topic, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_producewithfillandleak(randomleaktanks, count_leak, randomfilltanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_leaktank = 0
            index_filltank = 0
            lines[count] += 2
            while count < (len(lines) - 1):              
                if index_leaktank < count_leak and count == randomleaktanks[index_leaktank]:
                    lines[count] -= 1.0
                    lines[count] = max(lines[count], 0)
                    index_leaktank += 1
                if index_filltank < count_fill and count == randomfilltanks[index_filltank]:
                    lines[count] += 1.0
                    lines[count] = min(lines[count], 10)
                    index_filltank += 1
                if lines[count] == 0.0:
                    while count < (len(lines)-1):
                        mqtt_publish(str(lines[count]), topic, mqtt_client)
                        time.sleep(1)
                        count += 1
                else:              
                    lines[count] -= 1.0
                    lines[count+1] += 1.0
                    mqtt_publish(str(lines[count]), topic, mqtt_client)
                    time.sleep(1)
                    count += 1
            mqtt_publish(str(lines[count]), topic, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

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

def simulate_randomleak(randomtanks, count_leak, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            while count < len(lines):              
                if index_tank < count_leak and count == randomtanks[index_tank]:
                    lines[count] -= 1
                    lines[count] = max(lines[count], 0)
                    index_tank += 1
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randomfill(randomtanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            while count < len(lines):              
                if index_tank < count_fill and count == randomtanks[index_tank]:
                    lines[count] += 1
                    lines[count] = min(lines[count], 10)
                    index_tank += 1
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_fillwithhole(randomtanks, count_leak, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            while count < len(lines):              
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randomfillandleak(randomleaktanks, count_leak, randomfilltanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_leaktank = 0
            index_filltank = 0

            while count < len(lines):    
                if index_leaktank < count_leak and count == randomleaktanks[index_leaktank]:
                    lines[count] -= 1.0
                    lines[count] = max(lines[count], 0)
                    index_leaktank += 1
                if index_filltank < count_fill and count == randomfilltanks[index_filltank]:
                    lines[count] += 1.0
                    lines[count] = min(lines[count], 10)
                    index_filltank += 1          
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
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