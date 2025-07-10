from fastapi import FastAPI, HTTPException, Query, Path
import os
import json
from datetime import datetime, timezone
from mock_data import I3X_DATA
from typing import Optional, List
from models import (
    Namespace, ObjectType, ObjectInstanceMinimal, ObjectInstance,
    LastKnownValue, HistoricalValue
)

app = FastAPI(
    title="I3X API", 
    description="Industrial Information Interface eXchange API - RFC 001 Compliant",
    version="1.0.0"
)

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

config = load_config()

# RFC 4.1.1 - Namespaces
@app.get("/namespaces", response_model=List[Namespace])
def get_namespaces():
    """Return array of Namespaces registered in the CMIP"""
    return I3X_DATA['namespaces']

# RFC 4.1.3 - Object Types
@app.get("/objectTypes", response_model=List[ObjectType])
def get_object_types(namespaceUri: Optional[str] = Query(default=None)):
    """Return array of Type definitions, optionally filtered by NamespaceURI"""
    if namespaceUri:
        return [t for t in I3X_DATA['objectTypes'] if t['namespaceUri'] == namespaceUri]
    return I3X_DATA['objectTypes']

# RFC 4.1.2 - Object Type Definition
@app.get("/objectType/{element_id}", response_model=ObjectType)
def get_object_type_definition(element_id: str = Path(...)):
    """Return JSON structure defining a Type for the requested ElementId"""
    for obj_type in I3X_DATA['objectTypes']:
        if obj_type['elementId'] == element_id:
            return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{element_id}' not found")

# RFC 4.1.4 - Relationship Types - Hierarchical
@app.get("/relationshipTypes/hierarchical", response_model=List[str])
def get_hierarchical_relationship_types():
    """Return hierarchical relationship types"""
    return I3X_DATA['relationships']['hierarchical']

# RFC 4.1.5 - Relationship Types - Non-Hierarchical
@app.get("/relationshipTypes/nonHierarchical", response_model=List[str])
def get_non_hierarchical_relationship_types():
    """Return non-hierarchical relationship types"""
    return I3X_DATA['relationships']['nonHierarchical']

# RFC 4.1.6 - Instances of an Object Type
@app.get("/instances")
def get_instances(
    typeId: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False)
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of instance objects, optionally filtered by Type ElementId"""
    instances = I3X_DATA['instances']
    if typeId:
        instances = [i for i in instances if i['typeId'] == typeId]
    
    if not includeMetadata:
        # Return minimal required metadata per RFC 3.1.1
        return [{
            "elementId": i["elementId"],
            "name": i["name"],
            "typeId": i["typeId"],
            "parentId": i["parentId"],
            "hasChildren": i["hasChildren"],
            "namespaceUri": i["namespaceUri"]
        } for i in instances]
    
    return instances

# RFC 4.1.8 - Object Definition
@app.get("/object/{element_id}")
def get_object_definition(
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False)
) -> ObjectInstance:
    """Return instance object by ElementId with current values"""
    for instance in I3X_DATA['instances']:
        if instance['elementId'] == element_id:
            if not includeMetadata:
                # Return minimal required metadata per RFC 3.1.1
                return {
                    "elementId": instance["elementId"],
                    "name": instance["name"],
                    "typeId": instance["typeId"],
                    "parentId": instance["parentId"],
                    "hasChildren": instance["hasChildren"],
                    "namespaceUri": instance["namespaceUri"],
                    "attributes": instance["attributes"]
                }
            return instance
    
    raise HTTPException(status_code=404, detail=f"Object '{element_id}' not found")

# RFC 4.1.7 - Objects linked by Relationship Type
@app.get("/relationships/{element_id}/{relationship_type}")
def get_related_objects(
    element_id: str = Path(...),
    relationship_type: str = Path(...),
    depth: int = Query(default=0),
    includeMetadata: bool = Query(default=False)
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of objects related by specified relationship type"""
    related_objects = []
    
    if relationship_type.lower() == "haschildren":
        related_objects = [i for i in I3X_DATA['instances'] if i.get('parentId') == element_id]
    elif relationship_type.lower() == "hasparent":
        for instance in I3X_DATA['instances']:
            if instance['elementId'] == element_id and instance.get('parentId'):
                parent = next((i for i in I3X_DATA['instances'] if i['elementId'] == instance['parentId']), None)
                if parent:
                    related_objects = [parent]
    
    if not includeMetadata:
        return [{
            "elementId": i["elementId"],
            "name": i["name"],
            "typeId": i["typeId"],
            "parentId": i["parentId"],
            "hasChildren": i["hasChildren"],
            "namespaceUri": i["namespaceUri"]
        } for i in related_objects]
    
    return related_objects

# RFC 4.2.1.1 - Object Element LastKnownValue
@app.get("/value/{element_id}", response_model=LastKnownValue)
def get_last_known_value(
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False)
):
    """Return current value for requested object by ElementId"""
    for instance in I3X_DATA['instances']:
        if instance['elementId'] == element_id:
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

# RFC 4.2.1.2 - Object Element HistoricalValue
@app.get("/history/{element_id}", response_model=List[HistoricalValue])
def get_historical_values(
    element_id: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False)
):
    """Return array of historical values for requested object by ElementId"""
    # Mock historical data - in real implementation this would query historical store
    for instance in I3X_DATA['instances']:
        if instance['elementId'] == element_id:
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

if __name__ == '__main__':
    import uvicorn
    
    port = config.get("port", 8080)
    debug = config.get("debug", False)
    host = config.get("host", "0.0.0.0")
    
    print(f"Starting server on {host}:{port} (debug: {debug})")
    uvicorn.run("app:app", host=host, port=port, reload=debug)
