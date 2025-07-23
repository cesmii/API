from fastapi import APIRouter, Path, Query, HTTPException, Body, Request
from typing import List, Optional
from datetime import datetime, timezone

from models import UpdateResult, UpdateRequest, HistoricalUpdateResult, HistoricalValueUpdate
from mock_data import I3X_DATA

ns_updates = APIRouter(prefix="", tags=["Update Methods"])

# RFC 4.2.2.1 - Object Element LastKnownValue
@ns_updates.put("/update", response_model=List[UpdateResult])
def update_elements(request: Request, update: UpdateRequest = Body(...)):
    if len(update.elementIds) != len(update.values):
        raise HTTPException(status_code=400, detail="elementIds and values arrays must be of the same length")
    
    results = []
    for element_id, value in zip(update.elementIds, update.values):
        # Find the instance
        instance = next((inst for inst in request.app.state.I3X_DATA['instances'] if inst['elementId'] == element_id), None)
        if not instance:
            results.append(UpdateResult(elementId=element_id, success=False, message="Element not found"))
            continue
        
        try:
            # Validate the write schema matches the instance schema
            value_schema = get_schema(value)
            instance_schema = get_schema(instance['attributes'])

            if (value_schema != instance_schema):
                raise Exception(f"Value schema does not match instance schema")

            instance['attributes'] = value
            instance['timestamp'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            results.append(UpdateResult(elementId=element_id, success=True, message="Updated successfully"))
        except Exception as e:
            results.append(UpdateResult(elementId=element_id, success=False, message=f"Update failed: {str(e)}"))
    
    return results

# TODO how do I stub this out and say "no supported"?
@ns_updates.put("/update/historical", response_model=List[HistoricalUpdateResult])
def update_historical_values(request: Request, updates: List[HistoricalValueUpdate]):
    raise HTTPException(status_code=501, detail="Historical updates not supported")


# Helper to get the schema for dictionaries
def get_schema(obj):
    if isinstance(obj, dict):
        return {k: get_schema(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        if not obj:
            return ["<empty>"]
        return [get_schema(obj[0])]
    else:
        return type(obj).__name__