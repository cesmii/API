#!/bin/bash
# Setup script to quickly initialize the virtual environment and run the server
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Create virtual environment if it doesn't exist
if [ ! -f $SCRIPT_DIR/venv ]; then
	echo Creating virtual environment...
	python -m venv venv #TODO - try py and python instead of python3? Can you get error output here
fi

# Activate virtual environment
echo Activating virtual environment...
chmod +x ./venv/bin/activate
./venv/bin/activate

# Install requirements
echo Install dependencies...
./venv/bin/pip3 install -r requirements.txt

# Run the server
echo Starting client...
./venv/bin/python3 qos0_test_client.py