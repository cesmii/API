from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectType, RelationshipType
from data_sources.data_interface import I3XDataSource

typeDefinitions = APIRouter(prefix="", tags=["Type Definitions"])


def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source


# RFC 4.1.2 - Object Type Definition
@typeDefinitions.get(
    "/objecttypes/{elementId}", response_model=ObjectType, tags=["Type Definitions"]
)
def get_object_type_definition(
    elementId: str = Path(...), data_source: I3XDataSource = Depends(get_data_source)
):
    """Return JSON structure defining a Type for the requested ElementId"""
    elementId = unquote(elementId)
    obj_type = data_source.get_object_type_by_id(elementId)
    if obj_type:
        return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{elementId}' not found")


# RFC 4.1.3 - Object Types
@typeDefinitions.get(
    "/objecttypes", response_model=List[ObjectType], tags=["Type Definitions"]
)
def get_object_types(
    namespaceUri: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Return array of Type definitions, optionally filtered by NamespaceURI"""
    return data_source.get_object_types(namespaceUri)


# RFC 4.1.4 - Relationship Types
# Return all the relationship types supported by the data source
@typeDefinitions.get(
    "/relationshiptypes",
    response_model=List[RelationshipType],
    tags=["Type Definitions"],
)
def get_relationship_types(
    namespaceUri: Optional[str] = Query(default=None),
    data_source: I3XDataSource = Depends(get_data_source),
):
    """Return array of relationship types, optionally filtered by NamespaceURI"""
    relationship_types = data_source.get_relationship_types()

    if namespaceUri:
        return [
            rt for rt in relationship_types if rt.get("namespaceUri") == namespaceUri
        ]

    return relationship_types
