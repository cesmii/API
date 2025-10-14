from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectInstanceMinimal, ObjectInstance, HistoricalValue
from data_sources.data_interface import I3XDataSource
from datetime import datetime, timezone

instances = APIRouter(prefix="", tags=["Instances"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.6 - Instances of an Object Type
@instances.get("/instances")
def get_instances(
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

@instances.get("/instances/{element_id}")
def get_instance_by_element_id(
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> ObjectInstanceMinimal | ObjectInstance:
    """Return an instance by its ElementId"""
    i = data_source.get_instance_by_id(element_id)
    
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

# RFC 4.2.1.2 - Object Element HistoricalValue
@instances.get("/instances/{element_id}/history", response_model=List[HistoricalValue])
def get_historical_values_by_element_id(
    element_id: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of historical values for requested object by ElementId"""
    element_id = unquote(element_id)
    # Mock historical data - in real implementation this would query historical store
    instance = data_source.get_instance_by_id(element_id)
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
    
    raise HTTPException(status_code=404, detail=f"Element '{element_id}' not found")