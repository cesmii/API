from datetime import datetime
import paho.mqtt.client as mqtt
from gpiozero import LED
from smip import graphql
import requests
import json

led1 = LED(26)						#GPIO Pin that the LED is on
mqtt_broker = "192.168.1.x"			#Address of the MQTT Broker
mqtt_topic = "your/topic"			#MQTT Topic to Listen On
mqtt_client = "YourClientName"		#A name for this MQTT Client
# Connection information for your SMIP Instance GraphQL endpoint
graphql = graphql("AuthenticatorName", "AuthenticatorPassword", "AuthenticatorUser", "AuthenticatorRole", "https://YOURINSTANCE.thinkiq.net/graphql")
inmeeting_attribute_id = "10926"	#The Equipment Attribute ID in your SMIP model

print (f"Listening for MQTT messages on topic: {mqtt_topic} ...")

def make_datetime_utc():
	utc_time = str(datetime.utcnow())
	time_parts = utc_time.split(" ")
	utc_time = "T".join(time_parts)
	time_parts = utc_time.split(".")
	utc_time = time_parts[0] + "Z"
	return utc_time

def update_smip(light_on):
	print("Posting Data to CESMII Smart Manufacturing Platform...")
	print()
	smp_query = f"""
                mutation updateTimeSeries {{
                replaceTimeSeriesRange(
                    input: {{attributeOrTagId: "{inmeeting_attribute_id}", entries: [ {{timestamp: "{make_datetime_utc()}", value: "{light_on}", status: "1"}} ] }}
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
	print("Received MQTT message: ", msg)
	if msg == "on":
		led1.on()
		update_smip("true")
	elif msg == "off":
		led1.off()
		update_smip("false")
	else:
		print("No valid GPIO message")

client = mqtt.Client(mqtt_client)
client.connect(mqtt_broker)
client.loop_start()
client.subscribe(mqtt_topic)
client.on_message=on_message
client.loop_forever()
