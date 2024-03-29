import datetime, time, random
import config
import paho.mqtt.client as paho
import smiputils
import mqttutils
import json, csv
import random
import copy

verbose = config.smip["verbose"]
data_file = config.simulator["data_file"]
simulation_keys = []
simulation_data = []
machine_column = 1
station_column = 2

def debug(verbose, message, sleep=0):
        if verbose:
                print (message)
        if sleep:
                time.sleep(sleep)

#Show config
print("\nCESMII FIS Data Block Simulator")
print("===============================")
debug(verbose, "Verbose mode: on")

print("Using MQTT Broker: " + str(config.mqtt["broker"]))
print("Using Data File: " + data_file)

# Read in simulation data
with open(data_file, newline='') as f:
        # Read the first line of the CSV file to create attributes
        csv_reader = csv.reader(f)
        csv_headings = next(csv_reader)
        column_names = list(csv_headings)
        columns = 0
        # Add a timestamp column
        simulation_keys.append("Timestamp")
        # Figure out other columns
        for i in column_names:
                simulation_keys.append(i.strip())
                # Remember important columns
                if i.strip() == "Machine_ID":
                        machine_column = columns
                if i.strip() == "Station_ID":
                        station_column = columns
                columns += 1

        # Read the rest of the rows into memory
        for row in csv_reader:
                simulation_data.append(row)

# Debugging info
debug(verbose, "Data Rows: " + str(len(simulation_data)))
debug(verbose, "Machine ID Column: " + str(machine_column))
debug(verbose, "Station ID Column: " + str(station_column), 1)
print("===============================")
        
# MQTT Client
broker=config.mqtt["broker"]
port=config.mqtt["port"]
payload_topic=config.mqtt["payload_topic_root"]
def on_publish(client, userdata, result):
        print("Updating MQTT topic: " + str(userdata))
mqtt_client= paho.Client("cesmii_simulation_client")
mqtt_client.on_publish = on_publish

# Main Simulation Loop
sim_count = 0
machine_pool = [10]
machine_add_count = 0

while True:
        # Send a random event
        cursor = random.randint(0, len(simulation_data)-1)
        curr_row = copy.copy(simulation_data[cursor])

        # Shift columns to insert a timestamp
        curr_row.insert(0, int(datetime.datetime.utcnow().timestamp()))

        if (len(curr_row) != len(simulation_keys)):
                # This bug should be fixed, but just in case...
                debug(verbose, "Data columns in current row (" + str(len(curr_row)) + ") exceed expected keys (" + str(len(simulation_keys)) + "), row " + str(cursor) + " will be ignored")
        else:        
                use_machine_column = machine_column + 1
                use_station_column = station_column + 1
                # Substitute simulation values
                machine_id = curr_row[use_machine_column]
                station_id = curr_row[use_station_column]

                # Remember important types once discovered
                machine_type_id = None
                station_type_id = None

                # Start randomizing machine number after configured number of events
                if len(set(machine_pool)) <= config.simulator["max_machines"] and sim_count > 0 and sim_count % config.simulator["wait_between_machines"] == 0: # and machine_count >= config.simulator["wait_between_machines"]:
                        # Add a new machine
                        new_machine = machine_pool[len(machine_pool)-1] + 1
                        # Artificially bias the demo toward newer machines
                        for i in range(len(set(machine_pool))):
                                machine_pool.append(new_machine)
                        debug(verbose, "Adding new machine to pool: " + str(new_machine) + " with weight " + str(len(set(machine_pool))), 4)
                
                # Pick a random machine from pool to update
                machine_id = random.choice(machine_pool)
                curr_row[use_machine_column] = machine_id

                # Start randomizing station number right away (if configured)
                if config.simulator["num_stations_per_machine"] > 1 and sim_count > 1:
                        station_id = random.randint(1,  config.simulator["num_stations_per_machine"])
                        curr_row[use_station_column] = station_id

                # Build the topic, attach the payload, send to broker (unless simulating MQTT)
                #TODO Make topic format a config
                topic = payload_topic + "machine/" + str(machine_id) + "/station/" + str(station_id)
                payload_data = mqttutils.utils.make_json_payload(curr_row, simulation_keys)
                if config.mqtt['simulate_only'] != True:
                        mqtt_client.connect(broker, port)
                        mqtt_client.user_data_set(topic)
                        mqtt_client.publish(topic, payload_data)
                debug(verbose, topic)
                debug(verbose, payload_data)

                # Get ready for next loop
                next_sample_rate = random.randint(config.simulator["event_sample_min"],  config.simulator["event_sample_max"])
                sim_count += 1
                debug(verbose, "")
                debug(verbose, "Sim #" + str(sim_count) + " complete, Sleeping " + str(next_sample_rate) + "...")
                debug(verbose, "")
                time.sleep(next_sample_rate)