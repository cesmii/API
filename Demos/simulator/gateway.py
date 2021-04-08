import config   #copy config-example.py to config.py and set values
from datetime import datetime
import paho.mqtt.client as mqtt
from smip import graphql
import requests
import uuid
import json

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + "GW" + uuid
mqtt_topic = "tank"			#This should be enumerated, not hard coded

# Connection information for your SMIP Instance GraphQL endpoint
graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"])
write_attribute_id = "893"	#The Equipment Attribute ID to be updated in your SMIP model

print (f"Listening for MQTT messages on topic: {mqtt_topic} ...")

def make_datetime_utc():
	utc_time = str(datetime.utcnow())
	time_parts = utc_time.split(" ")
	utc_time = "T".join(time_parts)
	time_parts = utc_time.split(".")
	utc_time = time_parts[0] + "Z"
	return utc_time

def update_smip(sample_value):
	print("Posting Data to CESMII Smart Manufacturing Platform...")
	print()
	smp_query = f"""
                mutation updateTimeSeries {{
                replaceTimeSeriesRange(
                    input: {{attributeOrTagId: "{write_attribute_id}", entries: [ {{timestamp: "{make_datetime_utc()}", value: "{sample_value}", status: "1"}} ] }}
                    ) {{
                    clientMutationId,
                    json
                }}
                }}
            """
	smp_response = ""

	try:
		smp_response = graphql.post(smp_query)
	except requests.exceptions.HTTPError as e:
		print("An error occured accessing the SM Platform!")
		print(e)

	print("Response from SM Platform was...")
	print(json.dumps(smp_response, indent=2))
	print()

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	print("Received MQTT message: " + msg)
	update_smip(msg)

print ("MQTT Broker:  " + mqtt_broker)
print ("MQTT Client ID:  " + mqtt_clientid)
print ("Publish Topic:   " + mqtt_topic)

mqtt_client = mqtt.Client(mqtt_clientid)
mqtt_client.connect(mqtt_broker)
#mqtt_client.loop_start()
mqtt_client.subscribe(mqtt_topic)
mqtt_client.on_message=on_message
mqtt_client.loop_forever()
