from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Any, Callable
from datetime import datetime, timezone
import asyncio
import json
import time
import random

from pydantic import BaseModel, Field, ConfigDict
from models import CreateSubscriptionRequest, CreateSubscriptionResponse, RegisterMonitoredItemsRequest, SyncResponseItem, UnsubscribeRequest
from mock_data import I3X_DATA

ns_subscriptions = APIRouter(prefix="", tags=["Subscription Methods"])

# RFC 4.2.3.1 - Create Subscription
@ns_subscriptions.post("/subscribe", response_model=CreateSubscriptionResponse)
def create_subscription(request: Request, subscription: CreateSubscriptionRequest):
    """Register a client for a new subscription with specified QoS"""
    
    # Validate QoS
    if subscription.qos not in ["QoS0", "QoS2"]:
        raise HTTPException(status_code=400, detail="Unsupported QoS level. Only QoS0 and QoS2 are supported.")

    # For now make the subscription ID a simple index to make manual testing easy, but should be a UUID
    subscription_id = str(len(request.app.state.I3X_DATA_SUBSCRIPTIONS))
    new_sub = Subscription(
        subscriptionId=subscription_id,
        qos=subscription.qos,
        created=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    request.app.state.I3X_DATA_SUBSCRIPTIONS.append(new_sub)

    return CreateSubscriptionResponse(
        subscriptionId=subscription_id,
        message="Subscription created successfully"
    )

    return CreateSubscriptionResponse(
        subscriptionId=subscription_id,
        message="Subscription created successfully"
    )


# RFC 4.2.3.2 - Register Monitored Items
@ns_subscriptions.post("/subscribe/{subscription_id}/register")
async def register_monitored_items(request: Request, subscription_id: str, req: RegisterMonitoredItemsRequest):
    sub = next((s for s in request.app.state.I3X_DATA_SUBSCRIPTIONS if str(s.subscriptionId) == str(subscription_id)), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Validate that root elementIds exist
    invalid = [eid for eid in req.elementIds if not any(i['elementId'] == eid for i in I3X_DATA['instances'])]
    if invalid:
        raise HTTPException(status_code=404, detail=f"Invalid elementIds: {', '.join(invalid)}")

    # Collect all monitored elementIds including descendants
    all_element_ids = set()
    for eid in req.elementIds:
        tree = collect_instance_tree(eid, req.maxDepth, 0, I3X_DATA["instances"])
        all_element_ids.update([i["elementId"] for i in tree])

    # Update the subscription
    # TODO right not this is additive, but should there be a remove API call or this replaces?
    for eid in all_element_ids:
        if eid not in sub.monitoredItems:
            sub.monitoredItems.append(eid)

   # QoS0 setup
    if sub.qos == "QoS0":
        # If handler and streaming_response already exist, reuse them
        if sub.handler is not None and sub.streaming_response is not None:
            # Just update monitoredItems and return existing streaming response
            return sub.streaming_response

        # Otherwise create queue, loop, handler, and streaming response once
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        async def event_stream():
            while True:
                update = await queue.get()
                yield json.dumps([update]) + "\n"

        def push_update_to_client(update):
            asyncio.run_coroutine_threadsafe(queue.put(update), loop)

        sub.handler = push_update_to_client
        sub.event_loop = loop
        sub.streaming_response = StreamingResponse(event_stream(), media_type="application/json")

        return sub.streaming_response

    # QoS2 setup: initialize empty pending queue
    if sub.qos == "QoS2":
        return {"message": "Monitored items registered (QoS2). Use /sync to poll for changes."}

# RFC 4.2.3.3 Sync
@ns_subscriptions.post("/subscribe/{subscription_id}/sync", response_model=List[SyncResponseItem])
def sync_qos2(request: Request, subscription_id: str):
    """Sync changes for a QoS 2 subscription"""

    # Locate the subscription
    sub = next((s for s in request.app.state.I3X_DATA_SUBSCRIPTIONS if str(s.subscriptionId) == str(subscription_id)), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.qos != "QoS2":
        raise HTTPException(status_code=400, detail="Sync is only supported for QoS2 subscriptions")

    response = sub.pendingUpdates.copy()
    sub.pendingUpdates.clear()
    return response

# 4.2.3.4 Unsubscribe
@ns_subscriptions.post("/unsubscribe")
def unsubscribe(request: Request, req: UnsubscribeRequest):
    removed = []
    not_found = []

    for subscription_id in req.subscriptionIds:
        index = next((i for i, s in enumerate(request.app.state.I3X_DATA_SUBSCRIPTIONS) if str(s.subscriptionId) == str(subscription_id)), None)
        if index is not None:
            removed.append(request.app.state.I3X_DATA_SUBSCRIPTIONS[index].subscriptionId)
            request.app.state.I3X_DATA_SUBSCRIPTIONS.pop(index)
        else:
            not_found.append(subscription_id)

    return {
        "message": "Unsubscribe processed.",
        "unsubscribed": removed,
        "not_found": not_found
    }

# Subscription thread responsible creating updated for items being monitored.
# If QoS is QoS0, it will call the handler immediately to send updates
# if QoS is QoS2, it will store the updates in a pending dictionary to be sent on the /sync call
def subscription_worker(I3X_DATA_SUBSCRIPTIONS, I3X_DATA, running_flag):
    # Create a map of elementId to value for quick access
    instance_index = {i["elementId"]: i for i in I3X_DATA["instances"]}

    while running_flag["running"]:

        # Create random values
        for instance in I3X_DATA["instances"]:
            # Hack to skip instances with "static" in their elementId
            if "static" not in instance or instance["static"] == False:
                randomize_numeric_values(instance["attributes"])

        for sub in I3X_DATA_SUBSCRIPTIONS:
            if not sub.monitoredItems:
                continue

            # TODO - right now metadata is a monitored item level setting?
            #include_metadata = sub.get("includeMetadata", False)

            for eid in sub.monitoredItems:
                instance = instance_index.get(eid)
                if not instance:
                    continue

                # Skip static instances if they are not meant to be monitored
                if "static" in instance and instance["static"] == True:
                    continue

                update = {
                    "elementId": instance["elementId"],
                    "name": instance["name"],
                    "typeId": instance["typeId"],
                    "parentId": instance["parentId"],
                    "hasChildren": instance["hasChildren"],
                    "namespaceUri": instance["namespaceUri"],
                    "value": instance["attributes"],
                    "timestamp": instance.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")) 
                }

                #if include_metadata:
                #    update["dataType"] = "object"

                if sub.qos == "QoS0":
                    handler = sub.handler
                    if handler:
                        try:
                            handler(update)
                        except Exception as e:
                            print(f"[QoS0] Handler error: {e}")

                elif sub.qos == "QoS2":
                    sub.pendingUpdates.append(update)

        time.sleep(1)

# Not required, but showing what information is stored for simulated subscriptions
class Subscription(BaseModel):
    subscriptionId: int
    qos: str
    created: str
    monitoredItems: List[str] = []
    pendingUpdates: List[Any] = []  # For QoS2, list of values to send
    handler: Optional[Callable[[Any], None]] = None  # For QoS0
    event_loop: Optional[Any] = None  # asyncio.AbstractEventLoop
    streaming_response: Optional[StreamingResponse] = Field(default=None, exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True) # Needed to allow for StreamingResponse in the model

# Simulate data changes by changing numeric values in the data
def randomize_numeric_values(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)):
                # Change numeric value randomly +/- up to 10%
                variation = v * 0.1
                new_val = v + random.uniform(-variation, variation)
                # If original was int, convert back to int
                obj[k] = int(new_val) if isinstance(v, int) else new_val
            elif isinstance(v, dict) or isinstance(v, list):
                randomize_numeric_values(v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, (int, float)):
                variation = item * 0.1
                new_val = item + random.uniform(-variation, variation)
                obj[i] = int(new_val) if isinstance(item, int) else new_val
            elif isinstance(item, dict) or isinstance(item, list):
                randomize_numeric_values(item)

# Recursively collect an instance tree starting from root_id
## TODO this should probably be a utility used by exploratory/browse as well?
def collect_instance_tree(root_id: str, max_depth: int = 0, depth: int = 0, instances=[]):
    collected = []
    for inst in instances:
        if inst['elementId'] == root_id:
            collected.append(inst)
            if inst.get('hasChildren') and (max_depth == 0 or depth < max_depth):
                children = [i for i in instances if i.get('parentId') == root_id]
                for child in children:
                    collected.extend(collect_instance_tree(child['elementId'], max_depth, depth + 1, instances))
    return collected