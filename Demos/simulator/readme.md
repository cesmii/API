# Install
sudo pip3 install paho-mqtt

# Run
`python3 simulate.py [config] [*optional* simulation-type] [*optional* topic-name]`
* config: name of config file to use, no extension. eg: tank
* simulation-type: the kind of simulation to perform, defaults to stepwise
  * stepwise: publishes each line of the config in a loop with a delay
  * random: determines the lowest and highest number in the config and publishes a random number in that range in a loop with a delay
* topic-name: the MQTT topic to publish under, if left blank, uses the value of config

# Stop
control + c
