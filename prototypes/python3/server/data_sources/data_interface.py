from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from models import Namespace, ObjectType, ObjectInstance

class I3XDataSource(ABC):
    """Abstract interface for I3X data sources"""
    
    @abstractmethod
    def start(self, update_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
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
    def get_object_types(self, namespace_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return array of Type definitions, optionally filtered by NamespaceURI"""
        pass
    
    @abstractmethod
    def get_object_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return JSON structure defining a Type for the requested ElementId"""
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
    def get_related_instances(self, element_id: str, relationship_type: str) -> List[Dict[str, Any]]:
        """Return array of objects related by specified relationship type"""
        pass
    
    @abstractmethod
    def get_hierarchical_relationships(self) -> List[str]:
        """Return hierarchical relationship types"""
        pass
    
    @abstractmethod
    def get_non_hierarchical_relationships(self) -> List[str]:
        """Return non-hierarchical relationship types"""
        pass
    
    @abstractmethod
    def update_instance_values(self, element_ids: List[str], values: List[Any]) -> List[Dict[str, Any]]:
        """Update values for specified element IDs"""
        pass
    
    @abstractmethod
    def get_all_instances(self) -> List[Dict[str, Any]]:
        """Return all instances (used by subscription worker)"""
        pass