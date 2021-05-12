# Install
* Requires Python3
* Requires Paho-MQTT:

```
sudo pip3 install paho-mqtt
```

* Modify line 8 to point to your MQTT Broker

# Simulator 
The simulator is intended to act like an independent process unit, emitting data over MQTT about its current state.

## Config
* Copy `config-example.py` to `config.py`
* Specify the MQTT section to match your Broker

## Run
`python3 simulate.py [simulation-file] [`*optional*` simulation-type] [`*optional*` topic-name]` [`*optional*` num_simutank]`
* **simulation-file**: name of simulation config file to use, no extension. eg: tank
* **simulation-type**: the kind of simulation to perform, defaults to stepwise
  * stepwise: publishes each line of the config in a loop with a delay
  * random: determines the lowest and highest number in the config and publishes a random number in that range in a loop with a delay
  * randomfill: fills in the randomly selected tanks untill they are full(set as 10.0), increment the tank value by 1.0 at each round 
  * randomleak: has leaks in the randomly selected tanks untill they are empty, decrement the tank value by 1.0 at each round
  * randomfillandleak: fills in the randomly selected tanks untill they are full(set as 10.0), and has leaks in another set of randomly selected tanks untill they are empty
  * fillwithhole: fills in the randomly selected tanks that also leak
  * produce: simulates the assemblyline production by passing the product at each tank to the next tank for processing. The first tank contains the raw products, the last tank contains the final products, and the other tanks contain materials needed for processing at each step. the size of the first tank and the last tank is infinity while the others are of size 10.0
  * producewithleak: like the normal produce process but has leaks in the randomly selected tanks
  * producewithfill: like the normal produce process but fills in the randomly selected tanks until full
  * producewithfillandleak: like the normal produce process but fills in the randomly selected tanks until full and has leaks in other set of random tanks

* **topic-name**: the MQTT topic to publish under, if left blank, uses the value of config
* **num_simutank**: the number of the tanks that would be randomly selected to go through simulations like leaks and fills, defaults to 1 when not provided

### Examples:
* `python3 simulate.py tank`
* `python3 simulate.py tank random MyTank1`

### Notes:
You can run multiple instances, but make sure they each have a unique topic on the Broker!

## Test
* Use an app like [MQTT Explorer](http://mqtt-explorer.com/)
* Subscribe to the `#` topic in the Advanced settings
![MQTT Client Advanced](MQTTClient--Advanced.png "MQTT Client Advanced")
* Connect to the Broker, and watch the data come in
![MQTT Client](MQTTClient.png "MQTT Client")

## Stop

```
control + c
```

# Gateway
The Gateway functions as a "connector" from MQTT to the SM Innovation Platform, pumping data from a simulator to the Platform.

## Config
* Uses same config.py as Simulator, but update the SMIP section to match your GraphQL Authenticator.
* Update line 16 to match the Attribute id to update in the SMIP
  * Hard-coding is sad. We need to query for and/or create the equipment instance, then find the attribute to update programmatically.

## Run

```
python3 gateway.py
```

# Mosquitto
Eclipse Mosquitto is an open source (EPL/EDL licensed) message broker that implements the MQTT protocol versions 5.0, 3.1.1 and 3.1. Mosquitto is lightweight and is suitable for use on all devices from low power single board computers to full servers.

## [Mosquitto Debian repository for Raspberry Pi](https://mosquitto.org/blog/2013/01/mosquitto-debian-repository/) (currently Pi 3 B+)
After following these steps, Mosquitto will automatically be started on boot and available at `:1883`.

* To use the new repository you should first import the repository package signing key:

```
wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key  
sudo apt-key add mosquitto-repo.gpg.key  
```

* Then make the repository available to apt:

```
cd /etc/apt/sources.list.d/
```

* Then one of the following, depending on which version of debian you are using:

```
sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list  
sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list  
sudo wget http://repo.mosquitto.org/debian/mosquitto-buster.list  
```

* Then update apt information:

```
apt-get update
```

* Install Mosquitto and Mosquitto-Clients

```
apt-get install mosquitto mosquitto-clients
```

* For v2+: Create Mosquitto configuration file. All listeners now require authentication to be configured. This is with the exception of the case where no listener configuration is provided and hence the listener is bound to the loopback interface and will start in local only mode allowing only connections from clients running on the local machine. This means that `allow_anonymous` now defaults to `false`. If you currently have a broker running that has a listener configured in the configuration file, but has no other authentication configured and no explicit `allow_anonymous` setting, then your clients will be unable to connect after upgrading to Mosquitto 2.0.
For ease of setup, the following configuration is allowing anonymous connections. For other authentication options see [https://mosquitto.org/documentation/authentication-methods/](https://mosquitto.org/documentation/authentication-methods/).

```
cd /etc/mosquitto/
sudo cp conf.d/default.conf conf.d/anon.conf
sudo vi conf.d/anon.conf
```

Update the `anon.conf` to the following:

```
listener 1883
allow_anonymous true
```

* Install Uncomplicated Firewall to allow port 1883 outside of the Rasberry Pi

```
apt-get install ufw
```

* Enable the firewall

```
ufw enable
```

* Allow port 1883

```
ufw allow 1883
```

## Start the Mosquitto Broker using a configuration file from 

```
sudo mosquitto -c /etc/mosquitto/mosquitto.conf
```

## Start the Mosquitto Broker using a configuration file in background mode
```
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -d
```

## Testing the Mosquitto Server

* Start the command line subscriber:

```
mosquitto_sub -v -t 'test/topic'
```

* Publish test message with the command line publisher:

```
mosquitto_pub -t 'test/topic' -m 'helloWorld'
```

Both the subscriber and publisher connection messages should be seen in the broker terminal and the 
following should be seen in the subscriber terminal:

```
test/topic helloWorld
```

## Data Flow
```
client (running python example code) > broker (mosquitto) > client (MQTT Explorer)
```
