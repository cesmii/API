from fastapi import APIRouter, Path, Query, HTTPException, Request, Body, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectInstanceMinimal, ObjectInstance, HistoricalValue, UpdateResult, UpdateRequest, HistoricalUpdateResult, HistoricalValueUpdate
from data_sources.data_interface import I3XDataSource
from datetime import datetime, timezone

objects = APIRouter(prefix="", tags=["Objects"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.4 - Relationship Types
# Return all the relationship types supported by the data source
@objects.get("/relationshiptypes", tags=["Objects"]) 
def get_relationship_types(
    data_source: I3XDataSource = Depends(get_data_source)
) -> List[str]:
    """Return array of relationship types supported by the data source"""
    return data_source.get_relationship_types()

# RFC 4.1.5 - Instances of an Object Type
# Return all objects with a given typeId
@objects.get("/objects", tags=["Objects"])
def get_objects(
    typeId: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of instance objects, optionally filtered by Type ElementId"""
    instances = data_source.get_instances(typeId)
    
    if not includeMetadata:
        # Return minimal required metadata per RFC 3.1.1
        return [{
            "elementId": i["elementId"],
            "name": i["name"],
            "typeId": i["typeId"],
            "parentId": i["parentId"],
            "hasChildren": i["hasChildren"],
            "namespaceUri": i["namespaceUri"],
        } for i in instances]
    
    return instances


# 4.1.6 Objects linked by Relationship Type
# Return all the relationship types supported by the data source
@objects.get("/objects/{elementId}/related", tags=["Objects"])
def get_related_objects(
    elementId: str = Path(...),
    relationshiptype: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of related objects for the requested ElementId"""
    elementId = unquote(elementId)
    related_objects = data_source.get_related_instances(elementId, relationshiptype)
    return related_objects

# RFC 4.1.7 - Object Definition
# Return an object given it's elementId
@objects.get("/objects/{elementId}/definition", tags=["Objects"])
def get_objects_by_id(
    elementId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> ObjectInstanceMinimal | ObjectInstance:
    """Return an instance by its ElementId"""
    i = data_source.get_instance_by_id(elementId)
        
    # Check if instance was found, return 404 if not
    if not i:
        raise HTTPException(
            status_code=404, 
            detail=f"Instance with elementId '{element_id}' not found"
        )
    
    if not includeMetadata:
        # Return minimal required metadata per RFC 3.1.1
        return {
            "elementId": i["elementId"],
            "name": i["name"],
            "typeId": i["typeId"],
            "parentId": i["parentId"],
            "hasChildren": i["hasChildren"],
            "namespaceUri": i["namespaceUri"],
        }
    
    return i


# RFC 4.2.1.1 - [GET] Object Element LastKnown Value
@objects.get("/objects/{elementId}", tags=["Objects"])
def get_last_known_value(
    elementId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return current value for requested object by ElementId"""
    elementId = unquote(elementId)
    instance = data_source.get_instance_by_id(elementId)
    if instance:
        result = {
            "elementId": instance["elementId"],
            "value": instance["attributes"],
            "parentId": instance["parentId"],
            "hasChildren": instance["hasChildren"],
            "namespaceUri": instance["namespaceUri"]
        }
        
        if includeMetadata:
            result.update({
                "dataType": "object",
                "timestamp": instance.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            })
        
        return result
    
    raise HTTPException(status_code=404, detail=f"Element '{element_id}' not found")

# 4.2.2.1 [UPDATE] Object Element LastKnownValue
@objects.put("/objects", tags=["Objects"])
def update_object(update: UpdateRequest = Body(...), data_source: I3XDataSource = Depends(get_data_source)):
    if len(update.elementIds) != len(update.values):
        raise HTTPException(status_code=400, detail="elementIds and values arrays must be of the same length")
    
    return data_source.update_instance_values(update.elementIds, update.values)

# RFC 4.2.1.2 - [GET] Object Element HistoricalValue
@objects.get("/objects/{elementId}/history", response_model=List[HistoricalValue], tags=["Objects"])
def get_historical_values(
    elementId: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of historical values for requested object by ElementId"""
    elementId = unquote(elementId)
    # Mock historical data - in real implementation this would query historical store
    instance = data_source.get_instance_by_id(elementId)
    if instance:
        # Return mock historical data
        historical_values = [{
            "elementId": instance["elementId"],
            "value": instance["attributes"],
            "timestamp": instance.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
            "parentId": instance["parentId"],
            "hasChildren": instance["hasChildren"],
            "namespaceUri": instance["namespaceUri"]
        }]
        
        if includeMetadata:
            for hv in historical_values:
                hv["dataType"] = "object"
        
        return historical_values
    
    raise HTTPException(status_code=404, detail=f"Element '{objectId}' not found")

# RFC 4.2.2.2 - [UPDATE] Object Element HistoricalValue
@objects.put("/objects/history", tags=["Objects"])
def update_object_history(data_source: I3XDataSource = Depends(get_data_source)):
    """Modify the history of a specific instance resource"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )