from urllib.parse import unquote
from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from urllib.parse import unquote
from models import Namespace
from data_sources.data_interface import I3XDataSource
import logging

logger = logging.getLogger("uvicorn.error")  # or your module logger
ns = APIRouter(prefix="", tags=["Namespaces"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.1.1 - Namespaces
@ns.get("/namespaces", response_model=List[Namespace], tags=["Namespaces"])
def get_namespaces(data_source: I3XDataSource = Depends(get_data_source)):
    """Return array of Namespaces registered in the CMIP"""
    return data_source.get_namespaces()

from fastapi import HTTPException, status

@ns.get("/namespaces/{namespaceId}", response_model=Namespace, tags=["Namespaces"])
def get_namespace_by_id(
    namespaceId: str, 
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return a specific Namespace by its ID"""
    decoded_uri = unquote(namespaceId)
    namespaces = data_source.get_namespaces()
    nsFound = None

    for namespace in namespaces:
        logger.info("Looking for: %s", decoded_uri)
        logger.info("Namespace: %s", namespace)
        if namespace['uri'] == decoded_uri:
            nsFound = namespace

    if nsFound is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Namespace with ID '{namespaceId}' not found"
        )

    return nsFound    

