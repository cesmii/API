# Install
* Requires Python3
* Requires Paho-MQTT: `sudo pip3 install paho-mqtt`
* Modify line 8 to point to your MQTT Broker

# Run
`python3 simulate.py [config] [`*optional*` simulation-type] [`*optional*` topic-name]`
* **config**: name of config file to use, no extension. eg: tank
* **simulation-type**: the kind of simulation to perform, defaults to stepwise
  * stepwise: publishes each line of the config in a loop with a delay
  * random: determines the lowest and highest number in the config and publishes a random number in that range in a loop with a delay
* **topic-name**: the MQTT topic to publish under, if left blank, uses the value of config

Examples:
* `python3 simulate.py tank`
* `python3 simulate.py tank random MyTank1`

# Test
* Use an app like [MQTT Explorer](http://mqtt-explorer.com/), connect to the Broker, and watch the data come in

# Stop
`control + c`
