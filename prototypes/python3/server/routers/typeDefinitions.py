from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectType, RelationshipType
from data_sources.data_interface import I3XDataSource

typeDefinitions = APIRouter(prefix="", tags=["Explore"])


def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.3 - Object Types
@typeDefinitions.get(
    "/objecttypes", response_model=List[ObjectType], summary="Get Object Types"
)
def get_object_types(
    namespaceUri: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Get the schemas for all Types. Optionally filter by Namespace"""
    return data_source.get_object_types(namespaceUri)

# RFC 4.1.2 - Object Type Definition
@typeDefinitions.get(
    "/objecttypes/{elementId}", response_model=ObjectType, summary="Get Object Type"
)
def get_object_type_definition(
    elementId: str = Path(...), data_source: I3XDataSource = Depends(get_data_source)
):
    """Get the schema for a Type by its ElementID"""
    elementId = unquote(elementId)
    obj_type = data_source.get_object_type_by_id(elementId)
    if obj_type:
        return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{elementId}' not found")


# RFC 4.1.4 - Relationship Types
@typeDefinitions.get(
    "/relationshiptypes", response_model=List[RelationshipType], summary="Get Relationship Types"
)
def get_relationship_types(
    namespaceUri: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Get all Relationship Types. Optionally filtered by Namespace"""
    relationship_types = data_source.get_relationship_types()

    if namespaceUri:
        return [
            rt for rt in relationship_types if rt.get("namespaceUri") == namespaceUri
        ]

    return relationship_types

# RFC 4.1.4 - Relationship Type
@typeDefinitions.get(
    "/relationshiptypes/{elementId}", response_model=RelationshipType, summary="Get Relationship Type"
)
def get_relationship_type(
    elementId: str = Path(...), data_source: I3XDataSource = Depends(get_data_source),
):
    """Get a specific Relationship Type by its ElementID"""
    elementId = unquote(elementId)
    rel_type = data_source.get_relationship_type_by_id(elementId)
    if rel_type:
        return rel_type
    raise HTTPException(status_code=404, detail=f"Relationship type '{elementId}' not found")

    return [
        rt for rt in relationship_types if rt.get("namespaceUri") == namespaceUri
    ]

    return relationship_types
