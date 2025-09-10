#!/bin/bash
# Setup script to quickly initialize the virtual environment and run the server
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Create config file if it doesn't exist
if [ ! -d $SCRIPT_DIR/config.json ]; then
	echo Creating default config...
	cp config-example.json config.json
fi

# Create virtual environment if it doesn't exist
if [ ! -d $SCRIPT_DIR/venv ]; then
	echo Creating virtual environment...
	python3 -m venv venv
fi

# Activate virtual environment
echo Activating virtual environment...
source ./venv/bin/activate

# Install requirements
echo Install dependencies...
./venv/bin/pip3 install -r requirements.txt

# Run the server
echo Starting server...
./venv/bin/python3 app.py
