import unittest
from fastapi.testclient import TestClient
from app import app
from models import Namespace, ObjectType, ObjectInstanceMinimal

class TestI3XEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_namespaces_endpoint(self):
        """Test RFC 4.1.1 - Namespaces"""
        response = self.client.get('/namespaces')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)        
    
    def test_object_types_endpoint(self):
        """Test RFC 4.1.3 - Object Types"""
        response = self.client.get('/objectTypes')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
    def test_object_type_definition_endpoint(self):
        """Test RFC 4.1.2 - Object Type Definition"""
        response = self.client.get('/objectType/machine-type-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
        # Test non-existent type
        response = self.client.get('/objectType/non-existent')
        self.assertEqual(response.status_code, 404)
    
    def test_instances_endpoint(self):
        """Test RFC 4.1.6 - Instances of an Object Type"""
        response = self.client.get('/instances')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
    def test_object_definition_endpoint(self):
        """Test RFC 4.1.8 - Object Definition"""
        response = self.client.get('/object/machine-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
        # Test non-existent object
        response = self.client.get('/object/non-existent')
        self.assertEqual(response.status_code, 404)
    
    def test_last_known_value_endpoint(self):
        """Test RFC 4.2.1.1 - Object Element LastKnownValue"""
        response = self.client.get('/value/machine-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
        # Test with metadata
        response = self.client.get('/value/machine-001?includeMetadata=true')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        
    def test_hierarchical_relationships_endpoint(self):
        """Test RFC 4.1.4 - Relationship Types - Hierarchical"""
        response = self.client.get('/relationshipTypes/hierarchical')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
if __name__ == '__main__':
    unittest.main()
