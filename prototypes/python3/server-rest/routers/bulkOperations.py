from fastapi import APIRouter, Path, Query, HTTPException, Body, Request, Depends
from typing import List, Optional
from models import UpdateResult, UpdateRequest, UnsubscribeRequest
from data_sources.data_interface import I3XDataSource

bulk_ops = APIRouter(prefix="", tags=["Bulk Operations"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.2.2.1 - Object Element LastKnownValue
@bulk_ops.put("/bulkOps/updateInstances", response_model=List[UpdateResult])
def update_elements_in_bulk(update: UpdateRequest = Body(...), data_source: I3XDataSource = Depends(get_data_source)):
    if len(update.elementIds) != len(update.values):
        raise HTTPException(status_code=400, detail="elementIds and values arrays must be of the same length")
    
    return data_source.update_instance_values(update.elementIds, update.values)

# 4.2.3.4 Unsubscribe in Bulk
@bulk_ops.post("/bulkOps/unsubscribe")
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