# Smart Fridge Demo
This demo used Raspberry Pi GPIO sensors to instrument a fridge, and send data about environmental conditions to the SMIP.

See the video here: [https://www.youtube.com/watch?v=1q92ybO2ILE](https://www.youtube.com/watch?v=1q92ybO2ILE)

# Pre-requisites
- sudo apt install python3-gpiozero
- sudo pip3 install graphql_client

# Config
Edit common_graphql_functions.py to set the endpoint_uri to your platform instance
Edit insert_sample_data.py to change the tag and value you want to update

# Compatibility Issues
This demo pre-dates JWT-based authentication and would need to be modified for use on a current version of the SMIP.