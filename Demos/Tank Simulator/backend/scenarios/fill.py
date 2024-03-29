from utils import *

import paho.mqtt.client as mqtt
import config, json
import time

tank_volume = 0
pre_volume = 0
MAX_VOLUME = config.one_tank_size
tank_name = config.tank_name_prefix+"1"

def fill_tank(mqtt_client, flow_rate, set_fill):
    topic = tank_name
    time.sleep(1)
    global tank_volume
    global pre_volume

    tank_volume += flow_rate
    tank_volume = min(tank_volume, set_fill, MAX_VOLUME)
    tank_volume = round(tank_volume, 1)
    flow_rate = tank_volume - pre_volume
    pre_volume = tank_volume
    flow_rate = round(flow_rate, 1)
    jsonobj=make_default_json(tank_name, 0)

    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = flow_rate
    mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

    print("flow_rate: " + str(flow_rate))
    time.sleep(1)

def simulate_fill(flow_rate, set_fill, topic, mqtt_client):
    """Simulate fill with constant flow rate

    [description]
    
    Arguments:
        set_fill {float} -- the fill level where the fill stops
        flow_rate {float} -- the flow rate at which the tank is filled
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        jsonobj=make_default_json(tank_name, 0)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        while True:
            fill_tank(mqtt_client, flow_rate, set_fill)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
