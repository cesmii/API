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
    instances = data_source.get_instances(typeId)

    if not includeMetadata:
        # Return minimal required metadata per RFC 3.1.1
        return [
            {
                "elementId": i["elementId"],
                "name": i["name"],
                "typeId": i["typeId"],
                "namespaceUri": i["namespaceUri"],
                "parentId": i.get("parentId"),
                "hasChildren": i["hasChildren"],
            }
            for i in instances
        ]

    return instances

# RFC 4.1.7 - Object Definition
@explore.get("/objects/{elementId}", summary="Get Object")
def get_objects_by_id(
    elementId: str = Path(...),
    data_source: I3XDataSource = Depends(get_data_source),
) -> ObjectType:
    """Return an Object including it's value and metadata"""
    i = data_source.get_instance_by_id(elementId)

    # Check if instance was found, return 404 if not
    if not i:
        raise HTTPException(
            status_code=404, detail=f"Instance with elementId '{elementId}' not found"
        )

    find_type = i["typeId"]
    j = data_source.get_object_type_by_id(find_type)

    if not j:
        raise HTTPException(
            status_code=404, detail=f"Type with elementId '{elementId}' not found"
        )

    return j

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


# RFC 4.2.1.1 - [GET] Object Element LastKnown Value
@query.get("/objects/{elementId}/value", summary="Get Last Known Value")
def get_last_known_value(
    elementId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Return last known value for an Object"""
    elementId = unquote(elementId)
    instance = data_source.get_instance_values_by_id(elementId)
    if instance:
        result = instance

        if includeMetadata:
            result.update(
                {
                    "dataType": "object",
                    "timestamp": instance.get(
                        "timestamp",
                        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                }
            )

        return result

    raise HTTPException(status_code=404, detail=f"Element '{elementId}' not found")

# 4.2.2.1 [UPDATE] Object Element LastKnownValue
@update.put("/objects/{elementId}/value", summary="Update Value of Object")
def update_object(
    elementId: str = Path(...),
    body: Any = Body(...),  # Accept any JSON
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Update the value of an Object"""
    # Call update_instance_value with a single-element list
    return data_source.update_instance_value(elementId, body)


# RFC 4.2.1.2 - [GET] Object Element HistoricalValue
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
    # Mock historical data - in real implementation this would query historical store
    values = data_source.get_instance_values_by_id(elementId, startTime, endTime)
    if values:
        # Return mock historical data
        historical_values = values

        # Should always be a list
        if not isinstance(historical_values, list):
            historical_values = [historical_values]
        
        if includeMetadata:
            instance = data_source.get_instance_by_id(elementId)
            return {**instance, "values": historical_values}
        else:
            return historical_values

    raise HTTPException(status_code=404, detail=f"Element '{elementId}' not found")


# RFC 4.2.2.2 - [UPDATE] Object Element HistoricalValue
@update.put("/objects/{elementId}/history", summary="Update Historical Values of Object")
def update_object_history(elementId: str = Path(...),data_source: I3XDataSource = Depends(get_data_source)):
    """Update the historical values for one or more Objects"""
    raise HTTPException(status_code=501, detail="Operation not implemented")
