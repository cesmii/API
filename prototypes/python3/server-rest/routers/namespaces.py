from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import Namespace
from data_sources.data_interface import I3XDataSource

ns = APIRouter(prefix="", tags=["Namespaces"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.1 - Namespaces
@ns.get("/namespaces", response_model=List[Namespace], tags=["Namespaces"])
def get_namespaces(data_source: I3XDataSource = Depends(get_data_source)):
    """Return array of Namespaces registered in the CMIP"""
    return data_source.get_namespaces()