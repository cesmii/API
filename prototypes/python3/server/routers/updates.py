from fastapi import APIRouter, Path, Query, HTTPException, Body, Request, Depends
from typing import List, Optional
from datetime import datetime, timezone

from models import UpdateResult, UpdateRequest, HistoricalUpdateResult, HistoricalValueUpdate
from data_sources.data_interface import I3XDataSource

ns_updates = APIRouter(prefix="", tags=["Update Methods"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.2.2.1 - Object Element LastKnownValue
@ns_updates.put("/update", response_model=List[UpdateResult])
def update_elements(update: UpdateRequest = Body(...), data_source: I3XDataSource = Depends(get_data_source)):
    if len(update.elementIds) != len(update.values):
        raise HTTPException(status_code=400, detail="elementIds and values arrays must be of the same length")
    
    return data_source.update_instance_values(update.elementIds, update.values)

# TODO how do I stub this out and say "no supported"?
@ns_updates.put("/update/historical", response_model=List[HistoricalUpdateResult])
def update_historical_values(updates: List[HistoricalValueUpdate]):
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