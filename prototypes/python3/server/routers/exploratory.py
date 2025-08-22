from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from models import Namespace, ObjectType, ObjectInstanceMinimal, ObjectInstance
from data_sources.data_interface import I3XDataSource

ns_exploratory = APIRouter(prefix="", tags=["Exploratory Methods"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.1 - Namespaces
@ns_exploratory.get("/namespaces", response_model=List[Namespace], tags=["Exploratory Methods"])
def get_namespaces(data_source: I3XDataSource = Depends(get_data_source)):
    """Return array of Namespaces registered in the CMIP"""
    return data_source.get_namespaces()

# RFC 4.1.2 - Object Type Definition
@ns_exploratory.get("/objectType/{element_id}", response_model=ObjectType, tags=["Exploratory Methods"])
def get_object_type_definition(element_id: str = Path(...), data_source: I3XDataSource = Depends(get_data_source)):
    """Return JSON structure defining a Type for the requested ElementId"""
    obj_type = data_source.get_object_type_by_id(element_id)
    if obj_type:
        return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{element_id}' not found")

# RFC 4.1.3 - Object Types
@ns_exploratory.get("/objectTypes", response_model=List[ObjectType])
def get_object_types(namespaceUri: Optional[str] = Query(default=None), data_source: I3XDataSource = Depends(get_data_source)):
    """Return array of Type definitions, optionally filtered by NamespaceURI"""
    return data_source.get_object_types(namespaceUri)

# RFC 4.1.4 - Relationship Types - Hierarchical
@ns_exploratory.get("/relationshipTypes/hierarchical", response_model=List[str])
def get_hierarchical_relationship_types(data_source: I3XDataSource = Depends(get_data_source)):
    """Return hierarchical relationship types"""
    return data_source.get_hierarchical_relationships()

# RFC 4.1.5 - Relationship Types - Non-Hierarchical
@ns_exploratory.get("/relationshipTypes/nonHierarchical", response_model=List[str])
def get_non_hierarchical_relationship_types(data_source: I3XDataSource = Depends(get_data_source)):
    """Return non-hierarchical relationship types"""
    return data_source.get_non_hierarchical_relationships()

# RFC 4.1.6 - Instances of an Object Type
@ns_exploratory.get("/instances")
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
            "namespaceUri": i["namespaceUri"]
        } for i in instances]
    
    return instances

# RFC 4.1.7 - Objects linked by Relationship Type
@ns_exploratory.get("/relationships/{element_id}/{relationship_type}")
def get_related_objects(
    element_id: str = Path(...),
    relationship_type: str = Path(...),
    depth: int = Query(default=0),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> List[ObjectInstanceMinimal] | List[ObjectInstance]:
    """Return array of objects related by specified relationship type"""
    related_objects = data_source.get_related_instances(element_id, relationship_type)
    
    if not includeMetadata:
        return [{
            "elementId": i["elementId"],
            "name": i["name"],
            "typeId": i["typeId"],
            "parentId": i["parentId"],
            "hasChildren": i["hasChildren"],
            "namespaceUri": i["namespaceUri"],
            "relationshipType": i.get("relationType"),
            "relationshipTypeInverse": i.get("relationshipTypeInverse")
        } for i in related_objects]
    
    return related_objects

# RFC 4.1.8 - Object Definition
@ns_exploratory.get("/object/{element_id}")
def get_object_definition(
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
) -> ObjectInstance:
    """Return instance object by ElementId with current values"""
    instance = data_source.get_instance_by_id(element_id)
    if instance:
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
