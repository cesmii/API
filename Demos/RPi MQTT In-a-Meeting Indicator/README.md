# In-a-Meeting Indicator
This demo Raspberry Pi, running a MQTT client that can receive messages from a MQTT broker to turn on a LED connected to the GPIO. Valid messages are structured and sent to the SMIP for trending. Use it to record or indicate how much time you spend in meetings!

# Pre-requisites
- sudo pip install paho-mqtt
- sudo apt install python3-gpiozero

# Config
Edit common_graphql_functions.py to set the endpoint_uri to your platform instance
Edit insert_sample_data.py to change the tag and value you want to update