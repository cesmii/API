from utils import *

import paho.mqtt.client as mqtt
import random, config
import time
import math
import json

tank_volume = 0
time_counter = 0
absolute = False
MAX_VOLUME = config.one_tank_size
tank_name = config.tank_name_prefix+"1"

def change_tank(mqtt_client, function_rate, set_fill):
    topic = tank_name
    global tank_volume
    global time_counter
    
    function_rate = function_rate.replace('t)', "*"+str(time_counter)+")")
    pre_tank_volume = tank_volume

    tank_volume = eval(function_rate)
    if absolute:
        tank_volume = abs(tank_volume) 
    tank_volume = min(tank_volume, set_fill)
    tank_volume = max(tank_volume, 0)
    tank_volume = min(tank_volume, MAX_VOLUME)
    flow_rate = tank_volume - pre_tank_volume

    tank_volume = round(tank_volume, 3)
    flow_rate = round(flow_rate, 3)

    jsonobj=make_default_json(tank_name, 0)
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = flow_rate
    mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

    print("flow_rate: " + str(flow_rate))
    time_counter += 1
    time.sleep(0.5)

def simulate_functionchange(function_rate, set_fill, topic, mqtt_client):
    """Simulate fill level changes like the input math function trend line

    [description]
    
    Arguments:
        flow_rate {float} -- the flow rate function at which the tank is filled
        set_fill {float} -- the fill limit
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        global absolute
        #function_rate = function_rate.replace('sin', "math.sin")
        function_rate = function_rate.replace('cos', "math.cos")
        function_rate = function_rate.replace('pi', "math.pi")

        if function_rate.find("|") != -1:
            function_rate = function_rate.replace('|', "")
            absolute = True
        
        while True:
            change_tank(mqtt_client, function_rate, set_fill);

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
