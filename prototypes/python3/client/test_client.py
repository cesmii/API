import asyncio
import httpx
import json

# TODO - created from qos0_test_client.py, WIP test client

BASE_URL = "http://localhost:8080"  # Change to your API base URL

#######################################
##### Test Client Helper Methods ######
#######################################
async def api_call(url: str = None, method: str = None, payrams: dict = None):
    """get executes a get request against
    :param method: http method, choose from GET, POST, and PUT
    :param url: complete url of API method being called, up to the ?
    :param payrams: params if GET request, payload if PUT/POST request. expects caller enforces expected input
    :return: response from calling url with associated method and passed payload/params
    """
    if url is None:
        raise TypeError("url cannot be None")
    if payrams is None:
        payrams = {}

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, params=payrams)
        elif method == "POST":
            response = await client.post(url, json=payrams)
        elif method == "PUT":
            response = await client.put(url, json=payrams)
        else:
            raise TypeError("method must be 'GET', 'POST', or 'PUT'")

        response.raise_for_status()
        return response.json()


#######################################
######## Exploratory Methods ##########
#######################################
async def get_namespaces():
    """get_namespaces calls Get Namespaces exploratory method
    :return: namespaces dict"""
    url = f"{BASE_URL}/namespaces"
    return await api_call(url, "GET")

async def get_object_type(element_id: str):
    """get_object_type calls Get Object Type Definition exploratory method
    :param element_id: element id
    :return: object type def dict"""
    if element_id is None:
        raise TypeError("element_id cannot be None")
    url = f"{BASE_URL}/objectType/{element_id}"
    return await api_call(url, "GET")

async def get_object_types(namespace_uri: str = None):
    """get_object_types calls Get Object Types Exploratory method
    :param namespace_uri: namespace uri, optional
    :return: object types dict
    """
    url = f"{BASE_URL}/objectTypes"
    params = {}
    if namespace_uri is not None:
        params["namespaceUri"] = namespace_uri
    return await api_call(url, "GET")

async def get_relationship_types(hierarchical: bool = True):
    """get_relationship_types calls Get Relationship Types exploratory method
    :param hierarchical: boolean, if true get hierarchical relationships, non-hierarchical if false
    :return: relationship types arr
    """
    url = f"{BASE_URL}/relationshipTypes"
    if hierarchical:
        url += "/hierarchical"
    else:
        url += "/nonHierarchical"
    return await api_call(url, "GET")

async def get_instances(type_id: str = None, include_metadata: bool = False):
    """get_instances calls Get Instances Exploratory method
    :param type_id: type id, optional
    :param include_metadata: boolean, if true get instances metadata, default false
    :return: instances dict
    """
    url = f"{BASE_URL}/instances"
    params = {}
    if type_id is not None:
        params["typeId"] = type_id
    if include_metadata:
        params['includeMetadata'] = "true"
    return await api_call(url, "GET", params)


async def get_relationships(element_id: str, relationship_type: str = None, depth: int = 0, include_metadata: bool = False):
    """get_relationships calls Get Relationships Exploratory method
    :param element_id: element id
    :param relationship_type: relationship type
    :param depth: depth, default 0
    :param include_metadata: boolean, if true get relationship metadata, default false
    :return: relationships dict"""
    url = f"{BASE_URL}/relationships"
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    if relationship_type is None:
        raise ValueError("relationship_type is required to run get_relationships")
    url += f"/{element_id}/{relationship_type}"
    params = {'depth': depth, 'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"
    return await api_call(url, "GET", params)

async def get_object (element_id: str, include_metadata: bool = False):
    """get_object calls Get Object Definition Exploratory method
    :param element_id: element id
    :param include_metadata: boolean, if true get object metadata, default false
    :return: object dict"""
    url = f"{BASE_URL}/object"
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    url += f"/{element_id}"
    params = {'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"
    return await api_call(url, "GET", params)

#######################################
########### Value Methods #############
#######################################
async def get_value(element_id: str = None, include_metadata: bool = False):
    """get_value calls Get Value Value method
    :param include_metadata: boolean, if true get object metadata, default false
    :param element_id: element id
    :return: value dict"""
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    url = f"{BASE_URL}/value/{element_id}"
    params = {'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"

    return await api_call(url, "GET", params)

async def get_history(element_id: str, include_metadata: bool = False, start_time: str = None, end_time: str = None ):
    """get_history calls Get History Exploratory method
    :param element_id: element id
    :param include_metadata: boolean, if true get history metadata, default false
    :param start_time: start time, optional
    :param end_time: end time, optional"""
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    url = f"{BASE_URL}/history/{element_id}"
    params = {include_metadata: "false"}
    if include_metadata:
        params['includeMetadata'] = "true"
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time

    return await api_call(url, "GET", params)

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


async def main():
    try:
        print(await get_history("sensor-001", include_metadata=True),"2025-01-07T10:15:30Z","2025-08-07T10:15:30Z")
    except Exception as e:
        print(f"an exception occurred: {e}")

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
