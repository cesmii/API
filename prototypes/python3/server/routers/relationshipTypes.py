from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import Union, Dict, List
from urllib.parse import unquote
from models import ObjectType
from data_sources.data_interface import I3XDataSource

relTypes = APIRouter(prefix="", tags=["Relationship Types"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

@relTypes.get("/relationshiptypes", response_model=List[str])
def get_relationships(
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of relationship types supported by the data source"""
    return data_source.get_relationship_types()