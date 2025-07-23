import unittest
from fastapi.testclient import TestClient
from app import app
from models import Namespace, ObjectType, ObjectInstanceMinimal
import threading
import time
import asyncio

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

    # TODO this probably belongs on the client side and is more than a unit test, placing here so I have a place to test QoS0
    def test_qos0_subscription_streaming(self):
        # Step 1: Create a QoS0 subscription
        response = self.client.post("/subscribe", json={"qos": "QoS0"})
        self.assertEqual(response.status_code, 200)
        subscription_id = response.json()["subscriptionId"]
        self.assertIsNotNone(subscription_id)

        # Step 2: Register monitored items and start streaming
        url = f"/subscribe/{subscription_id}/register"
        payload = {
            "elementIds": ["machine-001"]
        }

        # We will run the streaming request in a separate thread to allow timeout
        results = []

        def stream_reader():
            with self.client.stream("POST", url, json=payload) as stream_resp:
                self.assertEqual(stream_resp.status_code, 200)
                count = 0
                for line in stream_resp.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        print("Received chunk:", decoded)   # <-- Add this line to print
                        results.append(decoded)
                        count += 1
                        if count >= 3:  # read 3 update batches then stop
                            break

        thread = threading.Thread(target=stream_reader)
        thread.start()
        thread.join(timeout=10)

        # Check that we got streaming data and parseable JSON
        self.assertGreaterEqual(len(results), 1, "Did not receive any streaming updates")

        for chunk in results:
            data = json.loads(chunk)
            self.assertIsInstance(data, list)
            self.assertTrue(all("elementId" in update for update in data))
        
if __name__ == '__main__':
    unittest.main()
