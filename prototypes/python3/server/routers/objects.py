from fastapi import APIRouter, Path, Query, HTTPException, Request, Body, Depends
from typing import List, Optional, Any
from urllib.parse import unquote
from models import (
    ObjectInstanceMinimal,
    ObjectInstance,
    HistoricalValue,
    ObjectType,
    UpdateResult,
    UpdateRequest,
    HistoricalUpdateResult,
    HistoricalValueUpdate,
)
from data_sources.data_interface import I3XDataSource
from datetime import datetime, timezone
from .utils import getValue, getObject

explore = APIRouter(prefix="", tags=["Explore"])
query = APIRouter(prefix="", tags=["Query"])
update = APIRouter(prefix="", tags=["Update"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source


# RFC 4.1.5 - Instances of an Object Type
@explore.get("/objects", summary="Get Objects")
def get_objects(
    typeId: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source),
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return all Objects. Optionally filter by TypeId"""
    instances = [getObject(i, includeMetadata) for i in data_source.get_instances(typeId)]
    return instances
      

# RFC 4.1.5 - Single Object
@explore.get("/objects/{elementId}", summary="Get Object")
def get_objects_by_id(
    elementId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source),
) -> ObjectInstanceMinimal | ObjectInstance:
    """Return an Object including it's value and metadata"""
    instance = data_source.get_instance_by_id(elementId)

    # Check if instance was found, return 404 if not
    if not instance:
        raise HTTPException(
            status_code=404, detail=f"Instance with elementId '{elementId}' not found"
        )

    return getObject(instance, includeMetadata)

# 4.1.6 Objects linked by Relationship Type
@explore.get("/objects/{elementId}/related", summary="Get Related Objects")
def get_related_objects(
    elementId: str = Path(...),
    relationshiptype: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Return array of related objects for the requested ElementId"""
    elementId = unquote(elementId)
    related_objects = data_source.get_related_instances(elementId, relationshiptype)
    return related_objects


# RFC 4.2.1.1 - Object Element LastKnown Value
@query.get("/objects/{elementId}/value", summary="Get Last Known Value")
def get_last_known_value(
    elementId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Return last known value for an Object"""
    elementId = unquote(elementId)
    
    # Lookup instance to verify it exists
    instance = data_source.get_instance_by_id(elementId)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Element '{elementId}' not found")

    # Get the value. Some objects may not have a value
    value = data_source.get_instance_values_by_id(elementId)

    return getValue(value, includeMetadata)

# 4.2.2.1 Object Element LastKnownValue
@update.put("/objects/{elementId}/value", summary="Update Value of Object")
def update_object(
    elementId: str = Path(...),
    body: Any = Body(...),  # Accept any JSON
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Update the value of an Object"""
    # Call update_instance_value with a single-element list
    return data_source.update_instance_value(elementId, body)


# RFC 4.2.1.2 - Object Element HistoricalValue
@query.get("/objects/{elementId}/history", response_model=Any, summary="Get Historical Values")
def get_historical_values(
    elementId: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Get the historical values for one or more Objects"""
    elementId = unquote(elementId)
    
     # Lookup instance to verify it exists
    instance = data_source.get_instance_by_id(elementId)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Element '{elementId}' not found")

    # Mock historical data - in real implementation this would query historical store
    historical_values = data_source.get_instance_values_by_id(elementId, startTime, endTime)

    if not isinstance(historical_values, list):
        historical_values = [historical_values]

    if not includeMetadata:
        return historical_values

    metadata_array = [getValue(val, includeMetadata) for val in historical_values]
    return metadata_array

# RFC 4.2.2.2 - Object Element HistoricalValue
@update.put("/objects/{elementId}/history", summary="Update Historical Values of Object")
def update_object_history(elementId: str = Path(...),data_source: I3XDataSource = Depends(get_data_source)):
    """Update the historical values for one or more Objects"""
    raise HTTPException(status_code=501, detail="Operation not implemented")
