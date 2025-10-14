from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import Union, Dict, List
from urllib.parse import unquote
from models import ObjectType
from data_sources.data_interface import I3XDataSource

relTypes = APIRouter(prefix="", tags=["Relationship Types"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

@relTypes.get("/relationshipTypes", response_model=Union[List[str], Dict[str, List[str]]])
def get_relationships(
    fech_rel_type: str = Query(default="all", description="Type of relationships to fetch: all, hierarchical, or non-hierarchical"),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return relationship types based on the specified type"""
    
    if fech_rel_type == "all":
        # Fetch both hierarchical and non-hierarchical relationships
        hierarchical = data_source.get_hierarchical_relationships()
        non_hierarchical = data_source.get_non_hierarchical_relationships()
        return {
            "hierarchical": hierarchical,
            "non-hierarchical": non_hierarchical
        }
    # RFC 4.1.4 - Relationship Types - Hierarchical
    elif fech_rel_type == "hierarchical":
        return { "hierarchical": data_source.get_hierarchical_relationships() }
    # RFC 4.1.5 - Relationship Types - Non-Hierarchical
    elif fech_rel_type == "non-hierarchical":
        return { "non-hierarchical": data_source.get_non_hierarchical_relationships() }
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid fech_rel_type: {fech_rel_type}. Must be 'all', 'hierarchical', or 'non-hierarchical'"
        )