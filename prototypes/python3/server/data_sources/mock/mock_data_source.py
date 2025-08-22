from typing import List, Optional, Dict, Any
from ..data_interface import I3XDataSource
from .mock_data import I3X_DATA

class MockDataSource(I3XDataSource):
    """Mock data implementation of I3XDataSource"""
    
    def __init__(self):
        self.data = I3X_DATA
    
    def get_namespaces(self) -> List[Dict[str, Any]]:
        return self.data['namespaces']
    
    def get_object_types(self, namespace_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        if namespace_uri:
            return [t for t in self.data['objectTypes'] if t['namespaceUri'] == namespace_uri]
        return self.data['objectTypes']
    
    def get_object_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        for obj_type in self.data['objectTypes']:
            if obj_type['elementId'] == element_id:
                return obj_type
        return None
    
    def get_instances(self, type_id: Optional[str] = None) -> List[Dict[str, Any]]:
        instances = self.data['instances']
        if type_id:
            instances = [i for i in instances if i['typeId'] == type_id]
        return instances
    
    def get_instance_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        for instance in self.data['instances']:
            if instance['elementId'] == element_id:
                return instance
        return None
    
    def get_related_instances(self, element_id: str, relationship_type: str) -> List[Dict[str, Any]]:
        related_objects = []
        
        # Handle hierarchical relationships
        if relationship_type.lower() == "haschildren":
            related_objects = [i for i in self.data['instances'] if i.get('parentId') == element_id]
        elif relationship_type.lower() == "hasparent":
            for instance in self.data['instances']:
                if instance['elementId'] == element_id and instance.get('parentId'):
                    parent = next((i for i in self.data['instances'] if i['elementId'] == instance['parentId']), None)
                    if parent:
                        related_objects = [parent]
        # Handle non-hierarchical relationships dynamically
        else:
            related_objects = self._process_non_hierarchical_relations(element_id, relationship_type.lower())
        
        # Add relationship type metadata to each related object
        relationship_type_proper = self._get_proper_case_relationship(relationship_type)
        relationship_type_inverse = self._get_inverse_relationship(relationship_type_proper)
        
        for obj in related_objects:
            obj['relationType'] = relationship_type_proper
            obj['relationshipTypeInverse'] = relationship_type_inverse
        
        return related_objects
    
    def _get_proper_case_relationship(self, relationship_type: str) -> str:
        """Get the proper case relationship type from the data"""
        # Check hierarchical relationships
        for rel_type in self.data['relationships']['hierarchical'].keys():
            if rel_type.lower() == relationship_type.lower():
                return rel_type
        
        # Check non-hierarchical relationships
        for rel_type in self.data['relationships']['nonHierarchical'].keys():
            if rel_type.lower() == relationship_type.lower():
                return rel_type
        
        # Fallback to title case
        return relationship_type.title()
    
    def _get_inverse_relationship(self, relationship_type: str) -> str:
        """Get the inverse relationship type"""
        # Check hierarchical relationships
        if relationship_type in self.data['relationships']['hierarchical']:
            return self.data['relationships']['hierarchical'][relationship_type]
        
        # Check non-hierarchical relationships
        if relationship_type in self.data['relationships']['nonHierarchical']:
            return self.data['relationships']['nonHierarchical'][relationship_type]
        
        # Fallback
        return relationship_type
    
    def _process_non_hierarchical_relations(self, element_id: str, relationship_type: str) -> List[Dict[str, Any]]:
        """Dynamically determine relationships based on instance metadata and semantic patterns"""
        related_objects = []
        source_instance = self.get_instance_by_id(element_id)
        
        if not source_instance:
            return related_objects
        
        # Check if instance has explicit relationship metadata
        relationships_metadata = source_instance.get('relationships', {})
        if relationship_type in relationships_metadata:
            # Return instances based on explicit relationship declarations
            related_ids = relationships_metadata[relationship_type]
            related_objects = [i for i in self.data['instances'] if i['elementId'] in related_ids]
        
        return related_objects
    
    def get_hierarchical_relationships(self) -> List[str]:
        return list(self.data['relationships']['hierarchical'].keys())
    
    def get_non_hierarchical_relationships(self) -> List[str]:
        return list(self.data['relationships']['nonHierarchical'].keys())
    
    def update_instance_values(self, element_ids: List[str], values: List[Any]) -> List[Dict[str, Any]]:
        from datetime import datetime, timezone
        
        results = []
        for element_id, value in zip(element_ids, values):
            instance = self.get_instance_by_id(element_id)
            if not instance:
                results.append({
                    "elementId": element_id,
                    "success": False,
                    "message": "Element not found"
                })
                continue
            
            try:
                # Validate the write schema matches the instance schema
                value_schema = self._get_schema(value)
                instance_schema = self._get_schema(instance['attributes'])

                if value_schema != instance_schema:
                    raise Exception("Value schema does not match instance schema")

                instance['attributes'] = value
                instance['timestamp'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                results.append({
                    "elementId": element_id,
                    "success": True,
                    "message": "Updated successfully"
                })
            except Exception as e:
                results.append({
                    "elementId": element_id,
                    "success": False,
                    "message": f"Update failed: {str(e)}"
                })
        
        return results
    
    def _get_schema(self, obj):
        """Helper to get the schema for dictionaries"""
        if isinstance(obj, dict):
            return {k: self._get_schema(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            if not obj:
                return ["<empty>"]
            return [self._get_schema(obj[0])]
        else:
            return type(obj).__name__
    
    def get_all_instances(self) -> List[Dict[str, Any]]:
        return self.data['instances']
