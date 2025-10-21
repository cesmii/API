from fastapi import APIRouter, HTTPException, Request, Path
from fastapi.responses import StreamingResponse
from typing import List, Optional, Any, Callable
from datetime import datetime, timezone
import asyncio
import json
import time
from pydantic import BaseModel, Field, ConfigDict
from models import CreateSubscriptionRequest, CreateSubscriptionResponse
from models import RegisterMonitoredItemsRequest, SyncResponseItem
from models import GetSubscriptionsResponse, SubscriptionSummary
from data_sources.data_interface import I3XDataSource

# Not required, but showing what information is stored for simulated subscriptions
class Subscription(BaseModel):
    subscriptionId: int
    qos: str
    created: str
    monitoredItems: List[str] = []
    pendingUpdates: List[Any] = []  # For QoS2, list of values to send
    # Exclude these fields from JSON serialization/schema
    handler: Callable[[Any], None] | None = Field(exclude=True, default=None)
    event_loop: Any | None = Field(exclude=True, default=None)
    streaming_response: StreamingResponse | None = Field(exclude=True, default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True) # Needed to allow for StreamingResponse in the model


subs = APIRouter(prefix="", tags=["Subscriptions"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC ?.?.?.? - Get current Subscriptions
@subs.get("/subscriptions", response_model=GetSubscriptionsResponse, tags=["Subscriptions"])
def get_subscriptions(request: Request):
    subscriptions = request.app.state.I3X_DATA_SUBSCRIPTIONS
    subscription_ids = []
    for subscription in subscriptions:
        try:
            subscription_ids.append(SubscriptionSummary(
                subscriptionId=subscription.subscriptionId,
                qos=subscription.qos,
                created=subscription.created
            ))
        except AttributeError:
            # Skip if subscription doesn't have subscriptionId
            continue
    return GetSubscriptionsResponse(
        subscriptionIds=subscription_ids
    )

# RFC ?.?.?.? - Get current Subscriptions
@subs.get("/subscriptions/{subscription_id}", response_model=Subscription, tags=["Subscriptions"])
def get_subscription_by_id(request: Request, subscription_id: str = Path(...)):
    subscriptions = request.app.state.I3X_DATA_SUBSCRIPTIONS
    
    # Convert subscription_id to int for comparison (since Subscription.subscriptionId is int)
    try:
        sub_id = int(subscription_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription ID format")
    
    # Find the subscription with matching subscriptionId
    for subscription in subscriptions:
        if subscription.subscriptionId == sub_id:
            return subscription
    
    # Return 404 if subscription_id is not found
    raise HTTPException(
        status_code=404, 
        detail=f"Subscription with ID '{subscription_id}' not found"
    )

# RFC 4.2.3.1 - Create Subscription
@subs.post("/subscriptions", response_model=CreateSubscriptionResponse, tags=["Subscriptions"])
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

# RFC 4.2.3.2 - Register Monitored Items
@subs.post("/subscriptions/{subscription_id}/instances", tags=["Subscriptions"])
async def register_monitored_items(request: Request, subscription_id: str, req: RegisterMonitoredItemsRequest):
    sub = next((s for s in request.app.state.I3X_DATA_SUBSCRIPTIONS if str(s.subscriptionId) == str(subscription_id)), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Get data source
    data_source = request.app.state.data_source
    
    # Validate that root elementIds exist
    invalid = [eid for eid in req.elementIds if not data_source.get_instance_by_id(eid)]
    if invalid:
        raise HTTPException(status_code=404, detail=f"Invalid elementIds: {', '.join(invalid)}")

    # Collect all monitored elementIds including descendants
    all_element_ids = set()
    for eid in req.elementIds:
        tree = collect_instance_tree(eid, req.maxDepth, 0, data_source.get_all_instances())
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
@subs.post("/subscriptions/{subscription_id}/AckAndGetNew", response_model=List[SyncResponseItem], tags=["Subscriptions"])
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

# 4.2.3.4 Unsubscribe by SubscriptionId
@subs.delete("/subscriptions/{subscription_id}", tags=["Subscriptions"])
def delete_subscription(request: Request, subscription_id: str):
    removed = []
    not_found = []

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

@subs.delete("/subscriptions/{subscription_id}/instances", tags=["Subscriptions"])
def delete_subscription_instances(
    request: Request, 
    subscription_id: str = Path(...)
):
    """Delete all instances associated with the subscription ID"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

@subs.post("/subscriptions/{subscriptionID}/instances")
def create_subscription_instances(
    request: Request, 
    subscriptionID: str = Path(...)
):
    """Create instances associated with the subscription ID"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

@subs.post("/subscriptions/{subscriptionID}/stream")
def create_subscription_stream(
    request: Request, 
    subscriptionID: str = Path(...)
):
    """Create stream for the subscription ID"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

# Subscription thread responsible creating updated for items being monitored.
# If QoS is QoS0, it will call the handler immediately to send updates
# if QoS is QoS2, it will store the updates in a pending dictionary to be sent on the /sync call
def handle_data_source_update(update, I3X_DATA_SUBSCRIPTIONS):
    """Route updates from data sources to active subscriptions"""
    try:
        # Iterate through all active subscriptions
        for sub in I3X_DATA_SUBSCRIPTIONS:
            if not sub.monitoredItems:
                continue
            
            # Check if this update is for a monitored element
            element_id = update.get("elementId")
            if element_id and element_id in sub.monitoredItems:
                if sub.qos == "QoS0":
                    # Immediate delivery via handler
                    if sub.handler:
                        try:
                            sub.handler(update)
                        except Exception as e:
                            print(f"[QoS0] Handler error: {e}")
                elif sub.qos == "QoS2":
                    # Queue for later sync
                    sub.pendingUpdates.append(update)
    except Exception as e:
        print(f"Error routing data source update: {e}")

def subscription_worker(I3X_DATA_SUBSCRIPTIONS, running_flag):
    """Subscription worker thread - now just keeps the thread alive for QoS0 streaming"""
    while running_flag["running"]:
        # Just sleep - updates now come via callback from data sources
        time.sleep(1)

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