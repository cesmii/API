from fastapi import APIRouter, Path, Query, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone

from models import LastKnownValue, HistoricalValue
from mock_data import I3X_DATA

ns_values = APIRouter(prefix="", tags=["Value Methods"])

# RFC 4.2.1.1 - Object Element LastKnownValue
@ns_values.get("/value/{element_id}", response_model=LastKnownValue)
def get_last_known_value(
    request: Request,
    element_id: str = Path(...),
    includeMetadata: bool = Query(default=False)
):
    """Return current value for requested object by ElementId"""
    for instance in request.app.state.I3X_DATA['instances']:
        if instance['elementId'] == element_id:
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
    request: Request,
    element_id: str = Path(...),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    includeMetadata: bool = Query(default=False)
):
    """Return array of historical values for requested object by ElementId"""
    # Mock historical data - in real implementation this would query historical store
    for instance in request.app.state.I3X_DATA['instances']:
        if instance['elementId'] == element_id:
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