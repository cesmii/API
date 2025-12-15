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
from .utils import getSubscriptionValue


# Not required, but showing what information is stored for simulated subscriptions
class Subscription(BaseModel):
    subscriptionId: int
    qos: str
    created: str
    maxDepth: int = 1  # Depth to follow HasComponent relationships (0=infinite, 1=no recursion, N=recurse N levels)
    monitoredItems: List[str] = []
    pendingUpdates: List[Any] = []  # For QoS2, list of values to send
    # Exclude these fields from JSON serialization/schema
    handler: Callable[[Any], None] | None = Field(exclude=True, default=None)
    event_loop: Any | None = Field(exclude=True, default=None)
    streaming_response: StreamingResponse | None = Field(exclude=True, default=None)
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )  # Needed to allow for StreamingResponse in the model


subs = APIRouter(prefix="", tags=["Subscribe"])


def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source


# RFC 4.2.3.1 - Create Subscription
@subs.post("/subscriptions", response_model=CreateSubscriptionResponse)
def create_subscription(request: Request, subscription: CreateSubscriptionRequest):
    """Register a client for a new subscription with specified QoS"""

    # Validate QoS
    if subscription.qos not in ["QoS0", "QoS2"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported QoS level. Only QoS0 and QoS2 are supported.",
        )

    # For now make the subscription ID a simple index to make manual testing easy, but should be a UUID
    subscriptionId = str(len(request.app.state.I3X_DATA_SUBSCRIPTIONS))
    new_sub = Subscription(
        subscriptionId=subscriptionId,
        qos=subscription.qos,
        created=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    request.app.state.I3X_DATA_SUBSCRIPTIONS.append(new_sub)

    return CreateSubscriptionResponse(
        subscriptionId=subscriptionId, message="Subscription created successfully"
    )


# RFC 4.2.3.2 - Register Monitored Items
@subs.post("/subscriptions/{subscriptionId}/objects")
async def register_monitored_items(
    request: Request, subscriptionId: str, req: RegisterMonitoredItemsRequest
):
    sub = next(
        (
            s
            for s in request.app.state.I3X_DATA_SUBSCRIPTIONS
            if str(s.subscriptionId) == str(subscriptionId)
        ),
        None,
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Get data source
    data_source = request.app.state.data_source

    # Validate that root elementIds exist
    invalid = [eid for eid in req.elementIds if not data_source.get_instance_by_id(eid)]
    if invalid:
        raise HTTPException(
            status_code=404, detail=f"Invalid elementIds: {', '.join(invalid)}"
        )

    # Collect all monitored elementIds including descendants
    all_element_ids = set()
    for eid in req.elementIds:
        tree = collect_instance_tree(
            eid, req.maxDepth, 0, data_source.get_all_instances()
        )
        all_element_ids.update([i["elementId"] for i in tree])

    # Update the subscription
    # Store maxDepth preference from the request
    sub.maxDepth = req.maxDepth
    # TODO right now this is additive, currently need to call delete and re-create the subscription entirely to remove items.
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
                # Remove None values to match QoS2 behavior
                filtered_update = {k: v for k, v in update.items() if v is not None}
                yield json.dumps([filtered_update]) + "\n"

        def push_update_to_client(update):
            asyncio.run_coroutine_threadsafe(queue.put(update), loop)

        sub.handler = push_update_to_client
        sub.event_loop = loop
        sub.streaming_response = StreamingResponse(
            event_stream(), media_type="application/json"
        )

        return sub.streaming_response

    # QoS2 setup: initialize empty pending queue
    if sub.qos == "QoS2":
        return {
            "message": "Monitored items registered (QoS2). Use /sync to poll for changes."
        }


# RFC 4.2.3.3 Sync
@subs.post(
    "/subscriptions/{subscriptionId}/sync",
    response_model=List[SyncResponseItem],
    response_model_exclude_none=True
)
def sync_qos2(request: Request, subscriptionId: str):
    """Sync changes for a QoS 2 subscription"""

    # Locate the subscription
    sub = next(
        (
            s
            for s in request.app.state.I3X_DATA_SUBSCRIPTIONS
            if str(s.subscriptionId) == str(subscriptionId)
        ),
        None,
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.qos != "QoS2":
        raise HTTPException(
            status_code=400, detail="Sync is only supported for QoS2 subscriptions"
        )

    response = sub.pendingUpdates.copy()
    sub.pendingUpdates.clear()
    return response


# 4.2.3.4 Unsubscribe by SubscriptionId
@subs.delete("/subscriptions/{subscriptionId}")
def delete_subscription(request: Request, subscriptionId: str):
    removed = []
    not_found = []

    index = next(
        (
            i
            for i, s in enumerate(request.app.state.I3X_DATA_SUBSCRIPTIONS)
            if str(s.subscriptionId) == str(subscriptionId)
        ),
        None,
    )
    if index is not None:
        removed.append(request.app.state.I3X_DATA_SUBSCRIPTIONS[index].subscriptionId)
        request.app.state.I3X_DATA_SUBSCRIPTIONS.pop(index)
    else:
        not_found.append(subscriptionId)

    return {
        "message": "Unsubscribe processed.",
        "unsubscribed": removed,
        "not_found": not_found,
    }


# Subscription thread responsible creating updated for items being monitored.
# If QoS is QoS0, it will call the handler immediately to send updates
# if QoS is QoS2, it will store the updates in a pending dictionary to be sent on the /sync call
def handle_data_source_update(instance, value, I3X_DATA_SUBSCRIPTIONS, data_source):
    """Route updates from data sources to active subscriptions"""
    try:
        # Iterate through all active subscriptions
        for sub in I3X_DATA_SUBSCRIPTIONS:
            if not sub.monitoredItems:
                continue

            # Check if this update is for a monitored element
            element_id = instance.get("elementId")
            if element_id and element_id in sub.monitoredItems:

                # Get the payload using the subscription's maxDepth preference
                updateValue = getSubscriptionValue(instance, value, maxDepth=sub.maxDepth, data_source=data_source)


                if sub.qos == "QoS0":
                    # Immediate delivery via handler
                    if sub.handler:
                        try:
                            sub.handler(updateValue)
                        except Exception as e:
                            print(f"[QoS0] Handler error: {e}")
                elif sub.qos == "QoS2":
                    # Queue for later sync
                    sub.pendingUpdates.append(updateValue)
    except Exception as e:
        import traceback
        print(f"Error routing data source update: {e}\n{traceback.format_exc()}")


def subscription_worker(I3X_DATA_SUBSCRIPTIONS, running_flag):
    """Subscription worker thread - now just keeps the thread alive for QoS0 streaming"""
    while running_flag["running"]:
        # Just sleep - updates now come via callback from data sources
        time.sleep(1)


# Recursively collect an instance tree starting from root_id
## TODO this should probably be a utility used by exploratory/browse as well?
def collect_instance_tree(
    root_id: str, max_depth: int = 0, depth: int = 0, instances=[]
):
    collected = []
    for inst in instances:
        if inst["elementId"] == root_id:
            collected.append(inst)
            if inst.get("isComposition") and (max_depth == 0 or depth < max_depth):
                children = [i for i in instances if i.get("parentId") == root_id]
                for child in children:
                    collected.extend(
                        collect_instance_tree(
                            child["elementId"], max_depth, depth + 1, instances
                        )
                    )
    return collected
