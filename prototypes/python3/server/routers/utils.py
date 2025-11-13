from typing import Any
from datetime import datetime, timezone

def getObject(instance: Any, includeMetadata: bool) -> Any:
    """Helper to format object with or without metadata"""
    if includeMetadata:
        return instance

    noMetadataObject = {
        "elementId": instance["elementId"],
        "displayName": instance["displayName"],
        "typeId": instance["typeId"],
        "namespaceUri": instance["namespaceUri"],
        "parentId": instance.get("parentId"),
        "hasChildren": instance["hasChildren"]
    }
    return noMetadataObject
    
def getValue(value: Any, includeMetadata: bool) -> Any:
    """Helper to format value with or without metadata"""
    if not includeMetadata:
        return value

    metadataValue = {
        "dataType": "object",
        "quality": "GoodNoData" if not value else "Good",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": value
    }

    return metadataValue

def getValueMetadata(value: Any) -> Any:
    """Helper to extract metadata from value"""
    metadata = {
        "dataType": "object",
        "quality": "GoodNoData" if not value else "Good",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return metadata

def getSubscriptionValue(instance: Any, record: Any, includeMetadata: bool) -> Any:
    """
    Helper to get subscription value formatted with or without metadata.

    Args:
        instance: The instance object with elementId
        record: The record object with structure {value: ..., quality: ..., timestamp: ..., localTimestamp: ..., etc}
        includeMetadata: If True, include all record-level metadata fields; if False, only include value

    Returns:
        Dictionary with elementId and value, optionally with all record-level metadata fields
    """
    # Extract the actual value from the record structure
    # The value itself may be a primitive (67.1) or a complex object with its own fields
    actual_value = record.get("value") if isinstance(record, dict) else record

    # Start with elementId and value (value contains all its data, primitive or complex)
    updateValue = {
        "elementId": instance["elementId"],
        "value": actual_value
    }

    # If includeMetadata is True, add ALL record-level metadata fields
    if includeMetadata and isinstance(record, dict):
        # Add all fields from the record except "value" (which is already included)
        for key, val in record.items():
            if key != "value":
                updateValue[key] = val

    return updateValue


    
