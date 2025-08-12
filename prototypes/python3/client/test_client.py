import asyncio
import httpx
import json

# TODO - created from qos0_test_client.py, WIP test client

BASE_URL = "http://localhost:8080"  # Change to your API base URL

#######################################
##### Test Client Helper Methods ######
#######################################
""" DEPRECATED::
async def api_call(url: str = None, method: str = None, payrams: dict = None):
    """"""get executes a get request against
    :param method: http method, choose from GET, POST, and PUT
    :param url: complete url of API method being called, up to the ?
    :param payrams: params if GET request, payload if PUT/POST request. expects caller enforces expected input
    :return: response from calling url with associated method and passed payload/params
    """"""
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
"""
def get_user_selection(valid_selections: list[str] = None):
    """Gets user to select item from list of valid selections

    :param valid_selections: array of strings denoting valid selections
    :return: string user_selection from array of valid selections
    """
    if valid_selections is None:
        raise TypeError("valid_selections cannot be None")

    user_selection = input().strip()
    while user_selection.upper() not in valid_selections:
        print(f"Invalid input received. Received '{user_selection}'. Valid selections:{valid_selections}")
        user_selection = input().strip()

    return user_selection

def get_include_metadata():
    """Prompts user if they want to 'Include Metadata'

    :return: True if user selected to include metadata, false otherwise
    """
    print(f"Include Metadata? \n1: Yes\n2: No")
    user_selection_include_metadata = get_user_selection(["1", "2"])
    if user_selection_include_metadata == "1":
        return True
    else:
        return False

async def get(url: str = None, params: dict = None):
    """get executes a get request against
    :param url: complete url of API method being called, up to the ?
    :param params: params if GET request, payload if PUT/POST request. expects caller enforces expected input
    :return: response from calling url with associated method and passed payload/params
    """
    if url is None:
        raise TypeError("url cannot be None")
    if params is None:
        params = {}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

#######################################
######## Exploratory Methods ##########
#######################################
async def get_namespaces():
    """get_namespaces calls Get Namespaces exploratory method
    :return: namespaces dict"""
    url = f"{BASE_URL}/namespaces"
    return await get(url)

async def get_object_type(element_id: str):
    """get_object_type calls Get Object Type Definition exploratory method
    :param element_id: element id
    :return: object type def dict"""
    if element_id is None:
        raise TypeError("element_id cannot be None")
    url = f"{BASE_URL}/objectType/{element_id}"
    return await get(url)

async def get_object_types(namespace_uri: str = None):
    """get_object_types calls Get Object Types Exploratory method
    :param namespace_uri: namespace uri, optional
    :return: object types dict
    """
    url = f"{BASE_URL}/objectTypes"
    params = {}
    if namespace_uri is not None:
        params["namespaceUri"] = namespace_uri
    return await get(url)

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
    return await get(url)

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
    else:
        params['includeMetadata'] = "false"
    return await get(url, params)


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
    return await get(url, params)

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
    return await get(url, params)

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

    return await get(url, params)

async def get_history(element_id: str, start_time: str = None, end_time: str = None,include_metadata: bool = False ):
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

    return await get(url, params)

#######################################
########### Update Methods ############
#######################################
async def update(element_ids:[]=None,values:[]=None):
    """update calls Update Elements API methods
    :param element_ids:
    :param values:
    :return:
    """
    pass
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
    """
    try:
        print(await get_history("sensor-001", include_metadata=True),"2025-01-07T10:15:30Z","2025-08-07T10:15:30Z")
    except Exception as e:
        print(f"an exception occurred: {e}")
    """
    try:
        print("Welcome to the CESMII I3X API Test Client.")
        selections = "\n1: Exploratory Methods\n2: Value Methods\n3: Update Methods\n4: Subscription Methods \nX: Quit\n"

        ##### MAIN INPUT LOOP #####
        while True: #broken by user input
            print(f"\nPlease make a selection.{selections}")
            user_selection = get_user_selection(["1","2","3","4","X"])
            if user_selection == "X":
                quit()

            ##### EXPLORATORY METHODS #####
            elif user_selection == "1":
                while True:
                    print(f"Exploratory Methods\n0: Back\n1: Get Namespaces\n2: Get Object Type Definition\n3: Get Object Types\n4: Get Relationship Types\n5: Get Instances\n6: Get Related Objects\n7: Get Object Definition\nX: Quit\n")
                    user_selection_exploratory = get_user_selection(["0","1","2","3","4","5","6","7","8","9","X"])
                    if user_selection_exploratory == "X":
                        exit()
                    elif user_selection_exploratory == "0":
                        break
                    elif user_selection_exploratory == "1":
                        print(await get_namespaces())
                    elif user_selection_exploratory == "2":
                        object_type = input("Enter Object Type: ").strip()
                        try:
                            print(await get_object_type(object_type))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Object type {object_type} not found")
                            else:
                                raise e
                    elif user_selection_exploratory == "3":
                        print(await get_object_types())
                    elif user_selection_exploratory == "4":
                        print(f"Select Relationship Type\n1: Hierarchical\n2: Non-Hierarchical\n")
                        user_selection_relationship_types = get_user_selection(["1","2"])
                        print(await get_relationship_types((user_selection_relationship_types == "1")))
                    elif user_selection_exploratory == "5":
                        type_id = input("Enter Type ElementID (leave blank to return all instance objects): ").strip()
                        try:
                            print(await get_instances(type_id,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Type ID {type_id} not found")
                            else:
                                raise e
                    elif user_selection_exploratory == "6":
                        element_id = input("Enter ElementID (required): ").strip()
                        relationship_type = input("Enter Relationship Type (required, see 'Get Relationship Types'): ").strip()
                        query_depth = input("Enter Query Depth (optional, integer, default 0): ").strip()
                        try:
                            query_depth = int(query_depth) if query_depth else 0
                        except ValueError:
                            print(f"Query depth entered - '{query_depth}' - is invalid. must be an integer, defaulting to 0.")
                            query_depth = 0

                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' or Relationship Type '{relationship_type}' not found")
                            else:
                                raise e
                        print(await get_relationships(element_id,relationship_type,query_depth,get_include_metadata()))
                    elif user_selection_exploratory == "7":
                        element_id = input("Enter ElementID (required): ").strip()
                        try:
                            print(await get_object(element_id,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e

                    print("\n\n")

            ##### VALUE METHODS #####
            elif user_selection == "2":
                while True:
                    print(f"Value Methods\n0: Back\n1: Get Last Known Value\n2: Get Historical Values\nX: Quit\n")
                    user_selection_exploratory = get_user_selection(["0", "1", "2", "X"])
                    if user_selection_exploratory == "X":
                        exit()
                    elif user_selection_exploratory == "0":
                        break
                    elif user_selection_exploratory == "1":
                        element_id = input("Enter ElementID (required): ").strip()
                        try:
                            print(await get_value(element_id, get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e
                    elif user_selection_exploratory == "2":
                        element_id = input("Enter ElementID (required): ").strip()
                        start_time = input("Enter Start Time (optional): ").strip()
                        end_time = input("Enter End Time (optional): ").strip()
                        #TODO: Could use better error handling on start_time/end_time
                        if not start_time:
                            start_time = None
                        if not end_time:
                            end_time = None
                        try:
                            print(await get_history(element_id,start_time,end_time,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e
                        pass

                    print("\n\n")

            ##### UPDATE METHODS #####
            elif user_selection == "3":
                pass

            ##### SUBSCRIPTION METHODS #####
            elif user_selection == "4":
                pass


    except Exception as e:
        print(f"an exception occurred: {e}")
        exit()

    """
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
