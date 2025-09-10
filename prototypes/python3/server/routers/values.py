from fastapi import APIRouter, Path, Query, HTTPException, Request, Depends
from typing import List, Optional
from datetime import datetime, timezone
from urllib.parse import unquote

from models import LastKnownValue, HistoricalValue
from data_sources.data_interface import I3XDataSource

ns_values = APIRouter(prefix="", tags=["Value Methods"])

def get_data_source(request: Request) -> I3XDataSource:
    """Dependency to inject data source"""
    return request.app.state.data_source

# RFC 4.2.1.1 - Object Element LastKnownValue
@ns_values.get("/value/{element_id}", response_model=LastKnownValue)
def get_last_known_value(
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return current value for requested object by ElementId"""
    element_id = unquote(element_id)
    instance = data_source.get_instance_by_id(element_id)
    if instance:
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
@ns_values.get("/history/{element_id}", response_model=List[HistoricalValue])
def get_historical_values(
    element_id: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False),
    data_source: I3XDataSource = Depends(get_data_source)
):
    """Return array of historical values for requested object by ElementId"""
    element_id = unquote(element_id)
    # Mock historical data - in real implementation this would query historical store
    instance = data_source.get_instance_by_id(element_id)
    if instance:
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