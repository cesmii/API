import asyncio
import httpx
import json

# TODO - created from qos0_test_client.py, WIP test client

BASE_URL = "http://localhost:8080"  # Change to your API base URL
ELEMENT_ID = "machine-001"  # Change to the element ID you want to monitor

#######################################
######## Exploratory Methods ##########
#######################################
async def get_namespaces():
    """get_namespaces calls Get Namespaces exploratory method
    :return: namespaces dict
    """
    url = f"{BASE_URL}/namespaces"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        namespaces = response.json()
        return namespaces

async def get_object_type(element_id: str):
    """get_object_type calls Get Object Type Definition exploratory method
    :param element_id: element id
    :return: object type def dict
    """
    url = f"{BASE_URL}/objectType/{element_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        object_type = response.json()
        return object_type

async def get_object_types(namespace_uri: str = None):
    """get_object_types calls Get Object Types Exploratory method
    :param namespace_uri: namespace uri, optional
    :return: object types dict
    """
    url = f"{BASE_URL}/objectTypes"
    async with httpx.AsyncClient() as client:
        if namespace_uri is not None:
            response = await client.get(url, params={"namespaceUri": namespace_uri})
        else:
            response = await client.get(url)
        response.raise_for_status()
        object_types = response.json()
        return object_types

#TODO: add remaining explore methods

#######################################
########### Value Methods #############
#######################################
#TODO: add value methods

#######################################
########### Update Methods ############
#######################################
#TODO: add update methods

#######################################
######## Subscription Methods #########
#######################################
async def subscribe(qos: str):
    url = f"{BASE_URL}/subscribe"
    payload = {"qos": qos}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        subscription_id = response.json()["subscriptionId"]
        print(f"Created subscription with ID: {subscription_id}")
        return subscription_id

#TODO: add remaining subscription methods


#######################################
########## Client Functions ###########
#######################################
async def run_qos0_stream(subscription_id: int):
    url = f"{BASE_URL}/subscribe/{subscription_id}/register"
    payload = {
        "elementIds": [ELEMENT_ID],
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                print(f"Failed to register monitored items: {response.text}")
                return

            print(f"Connected to QoS0 streaming for subscription {subscription_id}. Listening for updates...\n")

            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        print("Received update batch:")
                        for update in data:
                            print(update)
                    except Exception as e:
                        print(f"Failed to decode JSON line: {line}, error: {e}")


async def main():
    print(await get_object_types("http://i3x.org/mfg/process"))

    """
    print(f"Welcome to the I3X API Test Client.\nPlease select mode of communication (TODO):\n1:QoS0\n2:QoS1\n3QoS3\nOr press X to quit.")
    
    
    user_selection = input()
    while(user_selection.upper() not in ["X","1","2","3"]):
        print("Invalid input received. Received '{user_selection}'. Valid selections:\n0:Quit\n1:QoS0\n2:QoS1\n3QoS3")
        user_selection = input()
    
    
    
    qos = None
    match user_selection.upper():
        case "X":
            quit()
        case "1":
            qos = "QoS0"
        case "2":
            qos = "QoS1"
        case "2":
            qos = "QoS2"
        case _:
            print("Unable to process input. Input received: '{user_selection}'. Please try again.")
            quit()
   
    
    subscription_id = await create_subscription(qos)
    await run_qos0_stream(subscription_id)
    """

if __name__ == "__main__":
    asyncio.run(main())
