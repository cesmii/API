import unittest
import json
from app import app

class TestBrowseEndpoint(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    def test_browse_endpoint(self):
        response = self.client.get('/browse')
        data = json.loads(response.data)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        self.assertIn('status', data)
        self.assertIn('data', data)
        self.assertIn('count', data)
        self.assertIn('timestamp', data)
        
        # Check data content
        self.assertEqual(data['status'], 'success')
        
        # Check I3X data structure
        i3x_data = data['data']
        self.assertIn('namespaces', i3x_data)
        self.assertIn('objectTypes', i3x_data)
        self.assertIn('instances', i3x_data)
        self.assertIn('relationships', i3x_data)
        
        # Check instances exist
        self.assertGreater(len(i3x_data['instances']), 0)
        
        # Check instance structure
        instance = i3x_data['instances'][0]
        self.assertIn('elementId', instance)
        self.assertIn('name', instance)
        self.assertIn('typeId', instance)
        self.assertIn('attributes', instance)

    def test_get_instance_endpoint(self):
        """Test retrieving a specific instance by elementId"""
        response = self.client.get('/browse/instance/machine-001')
        data = json.loads(response.data)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        self.assertIn('status', data)
        self.assertIn('data', data)
        self.assertIn('timestamp', data)
        
        # Check data content
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['elementId'], 'machine-001')
        self.assertEqual(data['data']['name'], 'CNC-101')
        
        # Test non-existent instance
        response = self.client.get('/browse/instance/non-existent')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['status'], 'error')
      

if __name__ == '__main__':
    unittest.main()
