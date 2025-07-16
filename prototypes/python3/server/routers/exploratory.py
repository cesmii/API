from fastapi import APIRouter, Path, Query, HTTPException, Request
from typing import List, Optional
from models import Namespace, ObjectType, ObjectInstanceMinimal, ObjectInstance
from mock_data import I3X_DATA

ns_exploratory = APIRouter(prefix="", tags=["Exploratory Methods"])

# RFC 4.1.1 - Namespaces
@ns_exploratory.get("/namespaces", response_model=List[Namespace], tags=["Exploratory Methods"])
def get_namespaces(request: Request):
    """Return array of Namespaces registered in the CMIP"""
    return request.app.state.I3X_DATA['namespaces']

# RFC 4.1.2 - Object Type Definition
@ns_exploratory.get("/objectType/{element_id}", response_model=ObjectType, tags=["Exploratory Methods"])
def get_object_type_definition(request: Request, element_id: str = Path(...)):
    """Return JSON structure defining a Type for the requested ElementId"""
    for obj_type in request.app.state.I3X_DATA['objectTypes']:
        if obj_type['elementId'] == element_id:
            return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{element_id}' not found")

# RFC 4.1.3 - Object Types
@ns_exploratory.get("/objectTypes", response_model=List[ObjectType])
def get_object_types(request: Request, namespaceUri: Optional[str] = Query(default=None)):
    """Return array of Type definitions, optionally filtered by NamespaceURI"""
    if namespaceUri:
        return [t for t in request.app.state.I3X_DATA['objectTypes'] if t['namespaceUri'] == namespaceUri]
    return request.app.state.I3X_DATA['objectTypes']

# RFC 4.1.4 - Relationship Types - Hierarchical
@ns_exploratory.get("/relationshipTypes/hierarchical", response_model=List[str])
def get_hierarchical_relationship_types(request: Request):
    """Return hierarchical relationship types"""
    return request.app.state.I3X_DATA['relationships']['hierarchical']

# RFC 4.1.5 - Relationship Types - Non-Hierarchical
@ns_exploratory.get("/relationshipTypes/nonHierarchical", response_model=List[str])
def get_non_hierarchical_relationship_types(request: Request):
    """Return non-hierarchical relationship types"""
    return request.app.state.I3X_DATA['relationships']['nonHierarchical']

# RFC 4.1.6 - Instances of an Object Type
@ns_exploratory.get("/instances")
def get_instances(
    request: Request,
    typeId: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False)
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of instance objects, optionally filtered by Type ElementId"""
    instances = request.app.state.I3X_DATA['instances']
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

# RFC 4.1.7 - Objects linked by Relationship Type
@ns_exploratory.get("/relationships/{element_id}/{relationship_type}")
def get_related_objects(
    request: Request,
    element_id: str = Path(...),
    relationship_type: str = Path(...),
    depth: int = Query(default=0),
    includeMetadata: bool = Query(default=False),
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of objects related by specified relationship type"""
    related_objects = []
    
    if relationship_type.lower() == "haschildren":
        related_objects = [i for i in request.app.state.I3X_DATA['instances'] if i.get('parentId') == element_id]
    elif relationship_type.lower() == "hasparent":
        for instance in request.app.state.I3X_DATA['instances']:
            if instance['elementId'] == element_id and instance.get('parentId'):
                parent = next((i for i in request.app.state.I3X_DATA['instances'] if i['elementId'] == instance['parentId']), None)
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

# RFC 4.1.8 - Object Definition
@ns_exploratory.get("/object/{element_id}")
def get_object_definition(
    request: Request,
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False),
) -> ObjectInstance:
    """Return instance object by ElementId with current values"""
    for instance in request.app.state.I3X_DATA['instances']:
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
                    "attributes": instance["attributes"],
                    "timestamp": instance["timestamp"]
                }
            return instance
    
    raise HTTPException(status_code=404, detail=f"Object '{element_id}' not found")