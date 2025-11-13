from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from models import Namespace, ObjectType, ObjectInstance


class I3XDataSource(ABC):
    """Abstract interface for I3X data sources"""

    @abstractmethod
    def start(
        self, update_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> None:
        """Initialize and start the data source connection"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop and cleanup the data source connection"""
        pass

    @abstractmethod
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Return array of Namespaces registered in the CMIP"""
        pass

    @abstractmethod
    def get_object_types(
        self, namespace_uri: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return array of Type definitions, optionally filtered by NamespaceURI"""
        pass

    @abstractmethod
    def get_object_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return JSON structure defining a Type for the requested ElementId"""
        pass

    @abstractmethod
    def get_relationship_types(self, namespace_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return relationship types"""
        pass

    @abstractmethod
    def get_relationship_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return relationship type by ElementId"""
        pass

    @abstractmethod
    def get_instances(self, type_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return array of instance objects, optionally filtered by Type ElementId"""
        pass

    @abstractmethod
    def get_instance_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return instance object by ElementId"""
        pass

    @abstractmethod
    def get_instance_values_by_id(
        self,
        element_id: str,
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
        includeMetadata: bool = False,
        returnHistory: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Return instance values by ElementId.

        Args:
            element_id: The element to get values for
            startTime: Optional start time for filtering
            endTime: Optional end time for filtering
            includeMetadata: If True, returns full record with quality and timestamp. If False, returns only the value field(s).
            returnHistory: If True and no time range specified, returns all historical values. If False, returns only most recent value.
        """
        pass

    @abstractmethod
    def get_related_instances(
        self, element_id: str, relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return array of objects related by specified relationship type. If relationship_type is None, return all related objects."""
        pass

    @abstractmethod
    def update_instance_value(
        self, element_id: str, value: Any
    ) -> List[Dict[str, Any]]:
        """Update values for specified element IDs"""
        pass

    @abstractmethod
    def get_all_instances(self) -> List[Dict[str, Any]]:
        """Return all instances (used by subscription worker)"""
        pass
