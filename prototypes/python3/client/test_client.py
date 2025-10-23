import asyncio
import httpx
import json
import jsonschema

#######################################
##### Schema Resolution Methods #######
#######################################
RESPONSE_TYPE_RELATIONSHIPS = "relationships"
RESPONSE_TYPE_INSTANCES = "instances"
SCHEMA_FOLDER = "../server/schemas/exploratory/"
SCHEMA_RELATIONSHIPS = "relationships-response.json"
SCHEMA_INSTANCES = "instances-response.json"

def validate_response(response: object = None, response_type: str = None):
    """
    :param response: JSON object, the response to validate
    :param response_type: string, type of response indicating schema to validate against
    :return: True if response valid against schema, False otherwise
    """
    if response is None:
        raise TypeError("response cannot be None")
    if response_type is None:
        raise TypeError("response_type cannot be None")

    file_path = SCHEMA_FOLDER
    if response_type == RESPONSE_TYPE_RELATIONSHIPS:
        file_path += SCHEMA_RELATIONSHIPS
    elif response_type == RESPONSE_TYPE_INSTANCES:
        file_path += SCHEMA_INSTANCES
    else:
        raise TypeError("response_type " + response_type + " is not a valid response type")

    try:
        with open(file_path) as response_schema_file:
            response_schema = json.load(response_schema_file)
            jsonschema.validate(instance=response, schema=response_schema)
            return True
    except FileNotFoundError:
        print(f"Error: Could not validate response against schema. Schema file not found for response type {response_type}")
    except json.JSONDecodeError:
        print(f"Error: Could not validate response against schema. Schema JSON decoding failed for response type {response_type}")
    except jsonschema.ValidationError as e:
        print(f"Error: Validation of response against schema failed for response type {response_type}. Error:{e.message}")
    return False

#######################################
##### Test Client Helper Methods ######
#######################################
def pretty_print_json(data):
    """Pretty prints JSON data if it's valid JSON, otherwise prints as-is"""
    try:
        if isinstance(data, (dict, list)):
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(data)
    except (TypeError, ValueError):
        print(data)

def get_user_selection(valid_selections: list[str] = None):
    """Gets user to select item from list of valid selections

    :param valid_selections: array of strings denoting valid selections
    :return: string user_selection from array of valid selections
    """
    if valid_selections is None:
        raise TypeError("valid_selections cannot be None")

    user_selection = input().strip()
    while user_selection.upper() not in valid_selections:
        print(f"Invalid input received. Received '{user_selection}'. Valid selections:{valid_selections}. Please enter a valid selection.")
        user_selection = input().strip()

    return user_selection

def get_include_metadata():
    """Prompts user if they want to 'Include Metadata'

    :return: True if user selected to include metadata, false otherwise
    """
    user_selection_include_metadata = input(f"Include Metadata? (1: yes, else no): ").strip()
    if user_selection_include_metadata == "1":
        return True
    else:
        return False

async def get(url: str = None, params: dict = None):
    """get executes a get request against
    :param url: complete url of API method being called, up to the ?
    :param params: params for GET request. expects caller enforces expected input
    :return: response from calling url with associated method and passed params
    """
    if url is None:
        raise TypeError("url cannot be None")
    if params is None:
        params = {}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def put(url: str = None, payload: dict = None):
    """put executes a put request against url
    :param payload: JSON Payload to pass to put request
    :param url: complete url of API method being called
    :return: response returned from put request
    """
    if url is None:
        raise TypeError("url cannot be None")
    if payload is None:
        payload = {}

    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=payload)
        response.raise_for_status()
        return response.json()

async def post(url: str = None, payload: dict = None):
    """post executes a post request against url
    :param payload: JSON Payload to pass to post request
    :param url: complete url of API method being called
    :return: response returned from post request
    """
    if url is None:
        raise TypeError("url cannot be None")
    if payload is None:
        payload = {}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

#######################################
######## Exploratory Methods ##########
#######################################
async def get_namespaces(base_url: str = None):
    """get_namespaces calls Get Namespaces exploratory method
    :param base_url: base URL of API method being called
    :return: namespaces dict"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/namespaces"
    return await get(url)

async def get_object_type(base_url: str = None,element_id: str = None):
    """get_object_type calls Get Object Type Definition exploratory method
    :param base_url: base URL of API method being called
    :param element_id: element id
    :return: object type def dict"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if element_id is None:
        raise TypeError("element_id cannot be None")
    url = f"{base_url}/objectType/{element_id}"
    return await get(url)

async def get_object_types(base_url: str = None,namespace_uri: str = None):
    """get_object_types calls Get Object Types Exploratory method
    :param base_url: base URL of API method being called
    :param namespace_uri: namespace uri, optional
    :return: object types dict
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/objectTypes"
    params = {}
    if namespace_uri is not None:
        params["namespaceUri"] = namespace_uri
    return await get(url,params)

async def get_relationship_types(base_url: str = None):
    """get_relationship_types calls Get Relationship Types exploratory method
    :param base_url: base URL of API method being called
    :return: relationship types arr
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/relationshipTypes"
    return await get(url)

async def get_instances(base_url: str = None,type_id: str = None, include_metadata: bool = False):
    """get_instances calls Get Instances Exploratory method
    :param base_url: base URL of API method being called
    :param type_id: type id, optional
    :param include_metadata: boolean, if true get instances metadata, default false
    :return: instances dict
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/instances"
    params = {}
    if type_id is not None:
        params["typeId"] = type_id
    if include_metadata:
        params['includeMetadata'] = "true"
    else:
        params['includeMetadata'] = "false"

    json_response = await get(url, params=params)
    validate_response(json_response, RESPONSE_TYPE_INSTANCES)
    return json_response


async def get_relationships(base_url: str = None,element_id: str=None, relationship_type: str = None, depth: int = 0, include_metadata: bool = False):
    """get_relationships calls Get Relationships Exploratory method
    :param base_url: base URL of API method being called
    :param element_id: element id
    :param relationship_type: relationship type
    :param depth: depth, default 0
    :param include_metadata: boolean, if true get relationship metadata, default false
    :return: relationships dict"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/relationships"
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    if relationship_type is None:
        raise ValueError("relationship_type is required to run get_relationships")
    url += f"/{element_id}/{relationship_type}"
    params = {'depth': depth, 'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"

    json_response = await get(url, params=params)
    validate_response(json_response, RESPONSE_TYPE_RELATIONSHIPS)
    return json_response

async def get_object (base_url: str = None,element_id: str=None, include_metadata: bool = False):
    """get_object calls Get Object Definition Exploratory method
    :param base_url: base URL of API method being called
    :param element_id: element id
    :param include_metadata: boolean, if true get object metadata, default false
    :return: object dict"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/object"
    if element_id is None:
        raise ValueError("element_id is required to run get_object")
    url += f"/{element_id}"
    params = {'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"
    return await get(url, params)

#######################################
########### Value Methods #############
#######################################
async def get_value(base_url: str = None,element_id: str = None, include_metadata: bool = False):
    """get_value calls Get Value Value method
    :param base_url: base URL of API method being called
    :param include_metadata: boolean, if true get object metadata, default false
    :param element_id: element id
    :return: value dict"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    url = f"{base_url}/value/{element_id}"
    params = {'includeMetadata': "false"}
    if include_metadata:
        params['includeMetadata'] = "true"

    return await get(url, params)

async def get_history(base_url: str = None,element_id: str = None, start_time: str = None, end_time: str = None,include_metadata: bool = False ):
    """get_history calls Get History Exploratory method
    :param base_url: base url of API method being called
    :param element_id: element id
    :param include_metadata: boolean, if true get history metadata, default false
    :param start_time: start time, optional
    :param end_time: end time, optional"""
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if element_id is None:
        raise ValueError("element_id is required to run get_relationships")
    url = f"{base_url}/history/{element_id}"
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
async def update(base_url: str = None,element_ids: list[str] = None,values: list[str] = None, timestamps: list[str] = None):
    """update calls Update Elements API method
    :param base_url: base URL of API method being called
    :param element_ids: element ids to update, required
    :param values: values to update, required
    :param timestamps: timestamps to update, optional - if in place, updates historical values. Else, current value
    Indices of item across element ID/value/timestamps
    :return: JSON response from update
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/update"
    if element_ids is None or element_ids == []:
        raise ValueError("element_ids is required to run update")
    if values is None or values == []:
        raise ValueError("values is required to run update")
    if len(element_ids) != len(values):
        raise ValueError("element_ids and values must have same length")

    if timestamps is not None and timestamps != [] and len(timestamps) == len(values):
        updates = []
        for element_id, value, timestamp in zip(element_ids, values, timestamps):
            updates.append({
                "elementId": element_id,
                "value": value,
                "timestamp": timestamp
            })
        url += "/historical"
        payload = updates
    else:
        payload = {
            "elementIds": element_ids,
            "values": values,
        }
    return await put(url, payload)

#######################################
######## Subscription Methods #########
#######################################
async def subscribe(base_url: str = None,qos: str = None):
    """
    Calls Create Subscription API method
    :param base_url: base URL of API method being called
    :param qos: Subscription qos
    :return: Json response from subscribe (containing subscription ID)
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    url = f"{base_url}/subscribe"
    return await post(url, {"qos": qos})

async def register(base_url: str = None,subscription_id: str = None, element_ids: list[str] = None, include_metadata: bool = False, max_depth: int = 0):
    """
    register calls Register Monitored Items API method
    :param base_url: base URL of API method being called
    :param max_depth: Max depth of elements to register
    :param include_metadata: Include metadata if true, default false
    :param subscription_id: subscription id to register elements for
    :param element_ids: element ids to register
    :return: JSON response from register
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if subscription_id is None:
        raise ValueError("subscription_id is required to run register")
    if element_ids is None:
        raise ValueError("element_ids is required to run register")

    payload = {
        "elementIds": element_ids,
        "maxDepth": max_depth,
        "includeMetadata": include_metadata,
    }

    url = f"{base_url}/subscribe/{subscription_id}/register"

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        for update_received in data:
                            if update_received == 'message' and len(data) == 1:
                                return data # this is QoS2, return message to user
                            pretty_print_json(update_received)
                            # TODO: current state will run until program is killed externally. Add some threaded keyboard interrupt?
                    except Exception as e:
                        print(f"Failed to decode JSON line: {line}, error: {e}")

        return "" # if this is QoS0, handle prints here and have caller print nothing

async def sync(base_url: str = None,subscription_id: str = None):
    """
    sync calls Sync QoS2 API method
    :param base_url: base URL of API method being called
    :param subscription_id: subscription id to sync elements for
    :return: json response from sync
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if subscription_id is None:
        raise ValueError("subscription_id is required to run sync")
    url = f"{base_url}/subscribe/{subscription_id}/sync"
    return await post(url)

async def unsubscribe(base_url: str = None,subscription_ids: list[str] = None):
    """
    unsubscribe calls Unsubscribe Elements API method
    :param base_url: base URL of API method being called
    :param subscription_ids: array subscription ids to unsubscribe from
    :return: json response from unsubscribe
    """
    if base_url is None:
        raise TypeError("base_url cannot be None")
    if subscription_ids is None or subscription_ids == []:
        raise ValueError("subscription_ids is required to run unsubscribe")
    url = f"{base_url}/unsubscribe"
    return await post(url,{"subscriptionIds": subscription_ids})

#######################################
########## Client Functions ###########
#######################################
async def main():
    try:
        print("Welcome to the CESMII I3X API Test Client.")
        default_url = "http://localhost:8080"
        base_url = input(f"Enter the base url (or press enter to leave as default '{default_url}'): ").strip()
        if not base_url:
            base_url = default_url

        selections = "\n1: Exploratory Methods\n2: Value Methods\n3: Update Methods\n4: Subscription Methods \nX: Quit\n"

        ##### MAIN INPUT LOOP #####
        while True: #broken by user input
            print(f"\nPlease make a selection.{selections}")
            user_selection = get_user_selection(["1","2","3","4","X"])
            if user_selection.upper() == "X":
                exit()

            ##### EXPLORATORY METHODS #####
            elif user_selection == "1":
                while True:
                    print(f"Exploratory Methods\n0: Back\n1: Get Namespaces\n2: Get Object Type Definition\n3: Get Object Types\n4: Get Relationship Types\n5: Get Instances\n6: Get Related Objects\n7: Get Object Definition\nX: Quit\n")
                    user_selection = get_user_selection(["0","1","2","3","4","5","6","7","8","9","X"])
                    if user_selection.upper() == "X":
                        exit()
                    elif user_selection == "0":
                        break
                    elif user_selection == "1":
                        pretty_print_json(await get_namespaces(base_url))
                    elif user_selection == "2":
                        object_type = input("Enter Object Type: ").strip()
                        try:
                            pretty_print_json(await get_object_type(base_url, object_type))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Object type {object_type} not found")
                            else:
                                raise e
                    elif user_selection == "3":
                        namespace_uri = input("Enter namespace URI to filter on (optional, leave blank to return all): ").strip()
                        if not namespace_uri:
                            namespace_uri = None
                        pretty_print_json(await get_object_types(base_url, namespace_uri))
                    elif user_selection == "4":
                        pretty_print_json(await get_relationship_types(base_url))
                    elif user_selection == "5":
                        type_id = input("Enter Type ElementID (leave blank to return all instance objects): ").strip()
                        try:
                            pretty_print_json(await get_instances(base_url,type_id,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Type ID {type_id} not found")
                            else:
                                raise e
                    elif user_selection == "6":
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
                        pretty_print_json(await get_relationships(base_url,element_id,relationship_type,query_depth,get_include_metadata()))
                    elif user_selection == "7":
                        element_id = input("Enter ElementID (required): ").strip()
                        try:
                            pretty_print_json(await get_object(base_url,element_id,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e
                    print("\n")

            ##### VALUE METHODS #####
            elif user_selection == "2":
                while True:
                    print(f"Value Methods\n0: Back\n1: Get Last Known Value\n2: Get Historical Values\nX: Quit\n")
                    user_selection = get_user_selection(["0", "1", "2", "X"])
                    if user_selection.upper() == "X":
                        exit()
                    elif user_selection == "0":
                        break
                    elif user_selection == "1":
                        element_id = input("Enter ElementID (required): ").strip()
                        try:
                            pretty_print_json(await get_value(base_url, element_id, get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e
                    elif user_selection == "2":
                        element_id = input("Enter ElementID (required): ").strip()
                        start_time = input("Enter Start Time (optional): ").strip()
                        end_time = input("Enter End Time (optional): ").strip()
                        if not start_time:
                            start_time = None
                        if not end_time:
                            end_time = None
                        try:
                            pretty_print_json(await get_history(base_url, element_id,start_time,end_time,get_include_metadata()))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"ElementID '{element_id}' not found")
                            else:
                                raise e
                    print("\n")

            ##### UPDATE METHODS #####
            elif user_selection == "3":
                while True:
                    print(f"Update Methods\n0: Back\n1: Update Elements\n2: Update Historical Values\nX: Quit\n")
                    user_selection = get_user_selection(["0", "1", "2", "X"])
                    if user_selection.upper() == "X":
                        exit()
                    elif user_selection == "0":
                        break
                    elif user_selection == "1" or user_selection == "2":
                        element_ids = []
                        values = []
                        timestamps = None
                        if user_selection == "2": # TODO: historical updates currently not supported 8/11/25, untested
                            timestamps = [] # only used for user selection 2
                        while True:
                            element_id = input("Enter Element ID to update: ").strip()
                            value = input(f"Enter new value for Element ID '{element_id}': ").strip()
                            timestamp = None
                            if timestamps is not None:
                                timestamp = input(f"Enter timestamp to update for Element ID '{element_id}': ").strip()
                            try:
                                element_ids.append(element_id)
                                values.append(json.loads(value))
                                if timestamps is not None:
                                    timestamps.append(timestamp)
                            except ValueError:
                                print(f"Unable to parse value '{value}' as JSON, not adding element id/value to update.")

                            another = input("Enter another value? (1: yes, else no): ").strip()
                            if another != "1":
                                break

                        if element_ids != [] and values != []:
                            pretty_print_json(await update(base_url, element_ids,values,timestamps))
                    print("\n")

            ##### SUBSCRIPTION METHODS #####
            elif user_selection == "4":
                while True:
                    print(f"Subscription Methods\n0: Back\n1: Subscribe\n2: Register Monitored Items\n3: Sync QoS2 subscription\n4: Unsubscribe\nX: Quit\n")
                    user_selection = get_user_selection(["0","1","2","3","4","X"])
                    if user_selection.upper() == "X":
                        exit()
                    elif user_selection == "0":
                        break
                    elif user_selection == "1":
                        print("Choose Subscription Type:\n0: QoS0\n2: QoS2")
                        user_selection = get_user_selection(["0","2"])
                        qos = "QoS" + user_selection
                        pretty_print_json(await subscribe(base_url,qos))
                    elif user_selection == "2":
                        subscription_id = input("Enter Subscription ID: ").strip()
                        element_ids = []
                        while True:
                            element_id = input("Enter Element ID to register: ").strip()
                            element_ids.append(element_id)
                            another = input("Register another Element ID? (1: yes, else no): ").strip()
                            if another != "1":
                                break
                        max_depth = input("Enter Max Depth (optional, integer, default 0): ").strip()
                        try:
                            max_depth = int(max_depth) if max_depth else 0
                        except ValueError:
                            print(f"Max depth entered - '{max_depth}' - is invalid. must be an integer, defaulting to 0.")
                            max_depth = 0
                        try:
                            pretty_print_json(await register(base_url,subscription_id,element_ids,get_include_metadata(),max_depth))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Subscription ID '{subscription_id}' or element in '{element_ids}' not found")
                    elif user_selection == "3":
                        subscription_id = input("Enter Subscription ID: ").strip()
                        try:
                            pretty_print_json(await sync(base_url, subscription_id))
                        except Exception as e:
                            if str(e).startswith("Client error '404 Not Found' for url"):
                                print(f"Subscription ID '{subscription_id}' not found")
                    elif user_selection == "4":
                        subscription_ids = []
                        while True:
                            subscription_id = input("Enter Subscription ID to unsubscribe from: ").strip()
                            subscription_ids.append(subscription_id)
                            another = input("Enter another Subscription ID? (1: yes, else no): ").strip()
                            if another != "1":
                                break
                        pretty_print_json(await unsubscribe(base_url,subscription_ids))

    except Exception as e:
        print(f"an exception occurred: {e}")
        exit()

if __name__ == "__main__":
    asyncio.run(main())
