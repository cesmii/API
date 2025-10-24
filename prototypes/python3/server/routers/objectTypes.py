from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import ObjectType
from data_sources.data_interface import I3XDataSource

objectTypes = APIRouter(prefix="", tags=["Object Types"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.2 - Object Type Definition
@objectTypes.get("/objecttypes/{elementId}", response_model=ObjectType, tags=["Object Types"])
def get_object_type_definition(elementId: str = Path(...), data_source: I3XDataSource = Depends(get_data_source)):
    """Return JSON structure defining a Type for the requested ElementId"""
    elementId = unquote(elementId)
    obj_type = data_source.get_object_type_by_id(elementId)
    if obj_type:
        return obj_type
    raise HTTPException(status_code=404, detail=f"Object type '{elementId}' not found")

# RFC 4.1.3 - Object Types
@objectTypes.get("/objecttypes", response_model=List[ObjectType], tags=["Object Types"])
def get_object_types(namespaceUri: Optional[str] = Query(default=None), data_source: I3XDataSource = Depends(get_data_source)):
    """Return array of Type definitions, optionally filtered by NamespaceURI"""
    return data_source.get_object_types(namespaceUri)