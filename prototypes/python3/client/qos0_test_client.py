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

async def create_subscription():
    url = f"{BASE_URL}/subscribe"
    payload = {"qos": "QoS0"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        subscription_id = response.json()["subscriptionId"]
        print(f"Created subscription with ID: {subscription_id}")
        return subscription_id

async def main():
    subscription_id = await create_subscription()
    await run_qos0_stream(subscription_id)

if __name__ == "__main__":
    asyncio.run(main())
