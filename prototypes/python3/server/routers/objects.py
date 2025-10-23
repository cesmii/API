from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectInstanceMinimal, ObjectInstance, HistoricalValue
from data_sources.data_interface import I3XDataSource
from datetime import datetime, timezone

objects = APIRouter(prefix="", tags=["Objects"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.6 - Instances of an Object Type
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

@objects.get("/objects/{objectId}", tags=["Objects"])
def get_objects_by_id(
    objectId: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> ObjectInstanceMinimal | ObjectInstance:
    """Return an instance by its ElementId"""
    i = data_source.get_instance_by_id(objectId)
    
    # Print the content of variable 'i' to the console
    print(f"Content of 'i': {i}")
    
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

# New route: Get related objects by relationship type
@objects.get("/objects/{objectID}/related", tags=["Objects"])
def get_related_objects(
    objectId: str = Path(...),
    relationshiptype: Optional[str] = Query(default=None, alias="relationshiptype"),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return related instances for a given instance and relationship type"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

# New route: Get instance definition with metadata
@objects.get("/objects/{objectID}/definition", tags=["Objects"])
def get_object_definition(
    objectID: str = Path(...),
    includeMetadata: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return instance definition with optional metadata inclusion"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

# RFC 4.2.1.2 - Object Element HistoricalValue
@objects.get("/objects/{objectId}/history", response_model=List[HistoricalValue], tags=["Objects"])
def get_historical_values_by_objectId(
    objectId: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of historical values for requested object by ElementId"""
    objectId = unquote(objectId)
    # Mock historical data - in real implementation this would query historical store
    instance = data_source.get_instance_by_id(objectId)
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

# RFC 4.2.1.1 - Object Element LastKnown Value
@objects.put("/objects/{objectID}", tags=["Objects"])
def update_object(
    objectID: str = Path(...),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Modify the specified object resource"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

# RFC 4.2.1.1 - Object Element LastKnown Value in Bulk
@objects.put("/objects", tags=["Objects"])
def update_objects_bulk(
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Modify a list of instances in bulk"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )

# RFC 4.2.2.2 - Object Element HistoricalValue update
@objects.put("/objects/{objectID}/history", tags=["Objects"])
def update_object_history(
    objectID: str = Path(...),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Modify the history of a specific instance resource"""
    raise HTTPException(
        status_code=501, 
        detail="Operation not implemented"
    )