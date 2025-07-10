from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# RFC 4.1.1 - Namespace Model
class Namespace(BaseModel):
    uri: str = Field(..., description="Namespace URI")
    name: str = Field(..., description="Namespace name")

# Object Type Attribute Model
class ObjectTypeAttribute(BaseModel):
    name: str = Field(..., description="Attribute name")
    dataType: str = Field(..., description="JavaScript primitive data type")
    engUnit: Optional[str] = Field(None, description="Engineering unit (UNECE Rec 20)")

# RFC 4.1.2/4.1.3 - Object Type Model
class ObjectType(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the type")
    name: str = Field(..., description="Type name")
    namespaceUri: str = Field(..., description="Namespace URI")
    attributes: List[ObjectTypeAttribute] = Field(..., description="Type attributes")

# RFC 3.1.1 - Required Object Metadata (Minimal Instance)
class ObjectInstanceMinimal(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the element")
    name: str = Field(..., description="Object name")
    typeId: str = Field(..., description="ElementId of the object type")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(..., description="Boolean indicating if element has child objects")
    namespaceUri: str = Field(..., description="Namespace URI")

# RFC 3.1.1 + 3.1.2 - Full Object Instance with Attributes
class ObjectInstance(ObjectInstanceMinimal):
    attributes: Dict[str, Any] = Field(..., description="Object attribute values")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp")

# RFC 4.2.1.1 - Last Known Value Response
class LastKnownValue(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the element")
    value: Dict[str, Any] = Field(..., description="Current attribute values")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(..., description="Boolean indicating if element has child objects")
    namespaceUri: str = Field(..., description="Namespace URI")
    dataType: Optional[str] = Field(None, description="Data type (when includeMetadata=true)")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp (when includeMetadata=true)")

# RFC 4.2.1.2 - Historical Value Response
class HistoricalValue(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the element")
    value: Dict[str, Any] = Field(..., description="Historical attribute values")
    timestamp: str = Field(..., description="ISO 8601 timestamp when data was recorded")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(..., description="Boolean indicating if element has child objects")
    namespaceUri: str = Field(..., description="Namespace URI")
    dataType: Optional[str] = Field(None, description="Data type (when includeMetadata=true)")