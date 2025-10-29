from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime
from enum import Enum


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
    schema: JSONResponse = Field(..., description="Schema")
    # attributes: List[ObjectTypeAttribute] = Field(..., description="Type attributes")


# RFC 3.1.1 - Required Object Metadata (Minimal Instance)
class ObjectInstanceMinimal(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the element")
    name: str = Field(..., description="Object name")
    typeId: str = Field(..., description="ElementId of the object type")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(
        ..., description="Boolean indicating if element has child objects"
    )
    namespaceUri: str = Field(..., description="Namespace URI")


class ObjectLinkedByRelationshipType(BaseModel):
    subject: Optional[str] = Field(None, description="")
    relationshipType: Optional[str] = Field(
        None, description="Relationship type from source to this instance"
    )
    relationshipTypeInverse: Optional[str] = Field(
        None, description="Inverse relationship type from this instance to source"
    )
    elementId: str = Field(..., description="Unique string identifier for the element")
    name: str = Field(..., description="Object name")
    typeId: str = Field(..., description="ElementId of the object type")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(
        ..., description="Boolean indicating if element has child objects"
    )
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
    hasChildren: bool = Field(
        ..., description="Boolean indicating if element has child objects"
    )
    namespaceUri: str = Field(..., description="Namespace URI")
    dataType: Optional[str] = Field(
        None, description="Data type (when includeMetadata=true)"
    )
    timestamp: Optional[str] = Field(
        None, description="ISO 8601 timestamp (when includeMetadata=true)"
    )


# RFC 4.2.1.2 - Historical Value Response
class HistoricalValue(BaseModel):
    elementId: str = Field(..., description="Unique string identifier for the element")
    value: Dict[str, Any] = Field(..., description="Historical attribute values")
    timestamp: str = Field(..., description="ISO 8601 timestamp when data was recorded")
    parentId: Optional[str] = Field(None, description="ElementId of the parent object")
    hasChildren: bool = Field(
        ..., description="Boolean indicating if element has child objects"
    )
    namespaceUri: str = Field(..., description="Namespace URI")
    dataType: Optional[str] = Field(
        None, description="Data type (when includeMetadata=true)"
    )


# RFC 4.2.2.1 - Object Element LastKnownValue
class UpdateRequest(BaseModel):
    elementIds: List[str]
    values: List[Any]


# TODO: the RFC doesn't say what this should be
class UpdateResult(BaseModel):
    elementId: str
    success: bool
    message: str


# 4.2.2.2 Object Element HistoricalValue
class HistoricalValueUpdate(BaseModel):
    elementId: str
    timestamp: str  # ISO8601 string
    value: Any


class HistoricalUpdateResult(BaseModel):
    elementId: str
    timestamp: str
    success: bool
    message: str


class QoSLevel(str, Enum):
    fire_and_forget = "QoS0"
    guaranteed_delivery = "QoS2"


class CreateSubscriptionRequest(BaseModel):
    qos: QoSLevel


class CreateSubscriptionResponse(BaseModel):
    subscriptionId: str
    message: str


class RegisterMonitoredItemsRequest(BaseModel):
    elementIds: List[str]
    includeMetadata: Optional[bool] = False
    maxDepth: Optional[int] = 0  # 0 means no limit


class SyncResponseItem(BaseModel):
    elementId: str
    value: dict
    timestamp: str
    dataType: str = "object"
    name: str
    typeId: str
    parentId: Optional[str]
    hasChildren: bool
    namespaceUri: str


class UnsubscribeRequest(BaseModel):
    subscriptionIds: List[str]


class SubscriptionSummary(BaseModel):
    subscriptionId: int
    qos: str
    created: str


class GetSubscriptionsResponse(BaseModel):
    subscriptionIds: List[SubscriptionSummary]
