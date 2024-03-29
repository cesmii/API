from utils import *
import config
import time
import json
MAX_VOLUME = config.one_tank_size
tank_name = config.tank_name_prefix+"1"
def simulate_stepwise(lines, topic, mqtt_client):
    """Simulate fill level changes in the input file

    [description]
    
    Arguments:
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """
    try:
        topic = tank_name
        pre_volume = 0
        flowrate = 0
        jsonobj=make_default_json(tank_name, 0)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        while True:
            time.sleep(2)
            count = 0
            for line in lines:
                time.sleep(3)
                volume = round(float(line.strip()), 1)
                volume = min(volume, MAX_VOLUME)
                flowrate = volume - pre_volume
                pre_volume = volume
                jsonobj=make_default_json(tank_name, 0)
                jsonobj["flowrate"] = flowrate
                jsonobj["volume"] = volume
                jsonobj["temperature"] = volume * 2 + 3
                mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
                
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
