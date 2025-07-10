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
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Validate against Pydantic model
        namespaces = [Namespace(**item) for item in data]
        self.assertGreater(len(namespaces), 0)
    
    def test_object_types_endpoint(self):
        """Test RFC 4.1.3 - Object Types"""
        response = self.client.get('/objectTypes')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Validate against Pydantic model
        object_types = [ObjectType(**item) for item in data]
        self.assertGreater(len(object_types), 0)
    
    def test_object_type_definition_endpoint(self):
        """Test RFC 4.1.2 - Object Type Definition"""
        response = self.client.get('/objectType/machine-type-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['elementId'], 'machine-type-001')
        self.assertEqual(data['name'], 'CNCMachine')
        
        # Test non-existent type
        response = self.client.get('/objectType/non-existent')
        self.assertEqual(response.status_code, 404)
    
    def test_instances_endpoint(self):
        """Test RFC 4.1.6 - Instances of an Object Type"""
        response = self.client.get('/instances')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Validate against Pydantic model
        instances = [ObjectInstanceMinimal(**item) for item in data]
        self.assertGreater(len(instances), 0)
    
    def test_object_definition_endpoint(self):
        """Test RFC 4.1.8 - Object Definition"""
        response = self.client.get('/object/machine-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['elementId'], 'machine-001')
        self.assertIn('attributes', data)
        
        # Test non-existent object
        response = self.client.get('/object/non-existent')
        self.assertEqual(response.status_code, 404)
    
    def test_last_known_value_endpoint(self):
        """Test RFC 4.2.1.1 - Object Element LastKnownValue"""
        response = self.client.get('/value/machine-001')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['elementId'], 'machine-001')
        self.assertIn('value', data)
        
        # Test with metadata
        response = self.client.get('/value/machine-001?includeMetadata=true')
        data = response.json()
        self.assertIn('dataType', data)
        self.assertIn('timestamp', data)
    
    def test_hierarchical_relationships_endpoint(self):
        """Test RFC 4.1.4 - Relationship Types - Hierarchical"""
        response = self.client.get('/relationshipTypes/hierarchical')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertIn('HasParent', data)
        self.assertIn('HasChildren', data)
if __name__ == '__main__':
    unittest.main()
