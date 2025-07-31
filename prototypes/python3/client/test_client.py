import asyncio
import httpx
import json

# TODO - this is temporary, and should be replaced with a real test client. Right now it's used to test QoS0 streaming

BASE_URL = "http://localhost:8080"  # Change to your API base URL
ELEMENT_ID = "machine-001"  # Change to the element ID you want to monitor

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


### Exploratory Methods ###
async def get_namespaces():
    """get_namespaces calls get namespaces exploratory method

    :return: dictionary of namespace names to uris
    """
    url = f"{BASE_URL}/namespaces"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        namespaces = response.json()
        return namespaces

async def create_subscription(qos):


    url = f"{BASE_URL}/subscribe"
    payload = {"qos": qos}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        subscription_id = response.json()["subscriptionId"]
        print(f"Created subscription with ID: {subscription_id}")
        return subscription_id

async def main():
    print(get_namespaces())
    print(f"Welcome to the I3X API Test Client.\nPlease select mode of communication (TODO):\n1:QoS0\n2:QoS1\n3QoS3\nOr press X to quit.")
    

    user_selection = input()
    while(user_selection.upper() not in ["X","1","2","3"]):
        print("Invalid input received. Received '{user_selection}'. Valid selections:\n0:Quit\n1:QoS0\n2:QoS1\n3QoS3")
        user_selection = input()
    
    qos = QoS0
    """
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
   """"
    
    subscription_id = await create_subscription(qos)
    await run_qos0_stream(subscription_id)

if __name__ == "__main__":
    asyncio.run(main())
