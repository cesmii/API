import json
import logging
import re
import ssl
import threading
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from ..data_interface import I3XDataSource

class MQTTDataSource(I3XDataSource):
    """MQTT data source implementation with topic->value caching
    
    Creates an MQTT connection on start and subscribes to the topics set in config.json. 
    Keeps a cache of topic --> value to return exploratory and read interfaces. 
    Does not support Updates interface or the Exploratory hierarchy methods for now. 
    Supports Reads and Subscriptions.
    """
    
    # Define the MQTT namespace URI as a class constant
    MQTT_NAMESPACE_URI = "http://i3x.org/mfg/mqtt"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mqtt_endpoint = config.get('mqtt_endpoint', '')
        self.topics = config.get('topics', [])
        self.excluded_topics = config.get('excluded_topics', [])
        self.username = config.get('username')
        self.password = config.get('password')
        self.topic_cache = {}  # topic -> value cache
        self.cache_lock = threading.Lock()  # Thread-safe access to cache
        self.client = None
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
        self.update_callback = None
        
    def start(self, update_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """Initialize and start MQTT connection"""
        self.update_callback = update_callback
        if self.client is not None:
            return  # Already started
            
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Set username/password if provided
        if self.username is not None and self.password is not None:
            self.logger.info(f"Setting MQTT authentication for user: {self.username}")
            self.client.username_pw_set(self.username, self.password)
        
        # Parse MQTT endpoint (supports mqtt:// and mqtts:// for TLS)
        use_tls = False
        if self.mqtt_endpoint.startswith('mqtts://'):
            endpoint = self.mqtt_endpoint[8:]  # Remove mqtts:// prefix
            use_tls = True
            default_port = 8883
        elif self.mqtt_endpoint.startswith('mqtt://'):
            endpoint = self.mqtt_endpoint[7:]  # Remove mqtt:// prefix
            default_port = 1883
        else:
            raise ValueError(f"Invalid MQTT endpoint format: {self.mqtt_endpoint}. Use mqtt:// or mqtts://")
        
        # Extract host and port
        if ':' in endpoint:
            host, port = endpoint.split(':', 1)
            port = int(port)
        else:
            host = endpoint
            port = default_port
        
        # Configure TLS if needed
        if use_tls:
            self.logger.info(f"Configuring TLS for MQTT connection")
            # Create SSL context that accepts any certificate (insecure but simple)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.client.tls_set_context(context)
            
        self.logger.info(f"Connecting to MQTT broker at {host}:{port} (TLS: {use_tls})")

        try:
            self.client.connect(host, port, 60)
            self.client.loop_start()  # Start background thread
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker at {host}:{port}: {e}")
            raise
        
    def stop(self) -> None:
        """Stop and cleanup MQTT connection"""
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
        self.is_connected = False
        with self.cache_lock:
            self.topic_cache.clear()
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when MQTT client connects"""
        if rc == 0:
            self.is_connected = True
            self.logger.info("Successfully connected to MQTT broker")
            # Subscribe to all configured topics
            for topic in self.topics:
                self.logger.info(f"Subscribing to MQTT topic: {topic}")
                client.subscribe(topic)
            if self.topics:
                self.logger.info(f"Subscribed to {len(self.topics)} MQTT topics")
            else:
                self.logger.warning("No topics configured for MQTT subscription")
                
            # Clean up any excluded topics from existing cache after successful connection
            self._clean_excluded_topics_from_cache()
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when MQTT message is received"""
        try:
            # Check if topic should be excluded
            if self._is_topic_excluded(msg.topic):
                self.logger.debug(f"Skipping excluded topic: {msg.topic}")
                return
                
            # Try to parse as JSON, fallback to string
            try:
                value = json.loads(msg.payload.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                value = msg.payload.decode()

            # Update cache thread-safely
            with self.cache_lock:
                # Convert / to _ in topic for elementId to avoid URL path issues
                element_id = self._topic_to_element_id(msg.topic)
                timestamp = datetime.now(timezone.utc).isoformat()
                
                self.topic_cache[element_id] = {
                    'value': value,
                    'timestamp': timestamp,
                    'topic': msg.topic  # Keep original topic for reference
                }
                
                # If callback is set, notify subscription system of update
                if self.update_callback:
                    # Extract name from original topic
                    name = self._get_name_from_topic(msg.topic)
                    
                    update = {
                        "elementId": element_id,
                        "name": name,
                        "typeId": "",  # Empty for now
                        "parentId": "",  # Empty for now
                        "hasChildren": False,
                        "namespaceUri": self.MQTT_NAMESPACE_URI,
                        "value": value,
                        "timestamp": timestamp
                    }
                    
                    try:
                        self.update_callback(update)
                    except Exception as e:
                        self.logger.error(f"Error calling update callback: {e}")

        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when MQTT client disconnects"""
        self.is_connected = False
        if rc != 0:
            self.logger.warning(f"MQTT client disconnected unexpectedly with code {rc}")
        else:
            self.logger.info("MQTT client disconnected normally")
    
    def get_topic_value(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached value for a specific topic"""
        with self.cache_lock:
            return self.topic_cache.get(topic)
    
    def get_all_topic_values(self) -> Dict[str, Any]:
        """Get all cached topic values"""
        with self.cache_lock:
            return dict(self.topic_cache)

    # I3X Interface

    # For now just return a single hardcoded namespace
    def get_namespaces(self) -> List[Dict[str, Any]]:
        # TODO - should these be the topics we're subscribed to? what about #?
        return [{"uri": self.MQTT_NAMESPACE_URI, "name": "MQTT"}]

    # Since MQTT doesn't have types per topic, for now iterate all topics and create a type for each
    #   use the topic as the element ID for the type
    def get_object_types(self, namespace_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return array of Type definitions for all MQTT topics"""
        types = []
        
        with self.cache_lock:
            element_ids = list(self.topic_cache.keys())
        
        # Use get_object_type_by_id for each element_id
        for element_id in element_ids:
            type_definition = self.get_object_type_by_id(element_id)
            if type_definition is not None:
                # Apply namespace filtering if specified
                if namespace_uri is None or namespace_uri == self.MQTT_NAMESPACE_URI:
                    types.append(type_definition)
        
        self.logger.info(f"Generated {len(types)} type definitions")
        return types
    
    def get_object_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return JSON structure defining a Type built from MQTT topic data"""
        # Type definitions are stored in the cache without the suffix "_TYPE" but returned in queries with the suffix
        #   Remove it if its in the query so we get a match
        element_id = re.sub('_TYPE', '', element_id)
        with self.cache_lock:
            topic_data = self.topic_cache.get(element_id)
            if topic_data is None:
                self.logger.warning(f"No data found for element_id: {element_id}")
                return None
            
            # Get the current value to analyze its structure
            current_value = topic_data['value']
            original_topic = topic_data['topic']
            
            # Extract name from original topic
            type_name = self._get_name_from_topic(original_topic)
            
            # Build attributes array by analyzing the current value structure
            attributes = self._analyze_value_structure(current_value)
            
            type_definition = {
                "elementId": element_id + "_TYPE",
                "name": f"{type_name}Type",
                "namespaceUri": self.MQTT_NAMESPACE_URI,
                "attributes": attributes
            }
            
            self.logger.info(f"Generated type definition for {element_id}: {type_definition}")
            return type_definition

    def get_instances(self, type_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return array of instance objects, optionally filtered by type"""
        all_instances = self.get_all_instances()
        
        # If no type filter specified, return all instances
        if type_id is None:
            return all_instances
        
        # Filter by typeId
        filtered_instances = [instance for instance in all_instances if instance["typeId"] == type_id]
        self.logger.info(f"Filtered {len(all_instances)} instances to {len(filtered_instances)} matching typeId: {type_id}")
        return filtered_instances
    
    def get_instance_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Return instance object by ElementId (topic)"""
        self.logger.info(f"Looking up instance by ID: {element_id}")
        
        with self.cache_lock:
            self.logger.info(f"Available topics in cache: {list(self.topic_cache.keys())}")
            topic_data = self.topic_cache.get(element_id)
            
            if topic_data is None:
                self.logger.warning(f"No data found for topic: {element_id}")
                return None
            
            self.logger.info(f"Found data for topic '{element_id}': {topic_data}")
            
            # Extract name from last part of original topic path
            original_topic = topic_data['topic']
            name = self._get_name_from_topic(original_topic)
            
            instance = {
                "elementId": element_id,
                "name": name,
                "typeId": "",  # Empty for now
                "parentId": "",  # Empty for now  
                "hasChildren": False,
                "namespaceUri": self.MQTT_NAMESPACE_URI,
                "attributes": topic_data['value'],
                "timestamp": topic_data['timestamp']
            }
            
            self.logger.info(f"Returning instance: {instance}")
            return instance
    
    def get_related_instances(self, element_id: str, relationship_type: str) -> List[Dict[str, Any]]:
        """Return array of objects related by specified relationship type - placeholder"""
        return []
    
    def get_hierarchical_relationships(self) -> List[str]:
        """Return hierarchical relationship types - placeholder"""
        return []
    
    def get_non_hierarchical_relationships(self) -> List[str]:
        """Return non-hierarchical relationship types - placeholder"""
        return []
    
    def update_instance_values(self, element_ids: List[str], values: List[Any]) -> List[Dict[str, Any]]:
        """Update values for specified element IDs - placeholder"""
        return []
    
    def get_all_instances(self) -> List[Dict[str, Any]]:
        """Return all instances from MQTT topics"""
        instances = []
        
        with self.cache_lock:
            for element_id, topic_data in self.topic_cache.items():
                # Extract name from last part of original topic path
                original_topic = topic_data['topic']
                name = self._get_name_from_topic(original_topic)
                
                instance = {
                    "elementId": element_id,
                    "name": name,
                    "typeId": "",  # Empty for now
                    "parentId": "",  # Empty for now  
                    "hasChildren": False,
                    "namespaceUri": self.MQTT_NAMESPACE_URI,
                    "attributes": topic_data['value'],
                    "timestamp": topic_data['timestamp']
                }
                instances.append(instance)
        
        return instances
    

    # Helpers to respond to data source method calls above

    # Create a "type" definition based on the value on a payload
    def _analyze_value_structure(self, value: Any) -> List[Dict[str, Any]]:
        """Analyze a value and return attribute definitions"""
        attributes = []

        if isinstance(value, dict):
            # If value is a JSON object, create attributes for each key
            for key, val in value.items():
                attr = {
                    "name": key,
                    "dataType": self._get_data_type(val)
                }
                attributes.append(attr)
        else:
            # If value is primitive, create single "value" attribute
            attributes.append({
                "name": "value",
                "dataType": self._get_data_type(value)
            })

        return attributes

    # Convert value type to type definition. Do not traverse objects or arrays
    def _get_data_type(self, value: Any) -> str:
        """Map Python types to I3X data types"""
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, (dict, list)):
            return "object"
        else:
            return "string"  # Default fallback
    
    def _get_name_from_topic(self, topic: str) -> str:
        """Extract name from last part of topic path"""
        return topic.split('/')[-1] if '/' in topic else topic
    
    def _topic_to_element_id(self, topic: str) -> str:
        """Convert / to _ in topic for elementId to avoid URL path issues"""
        return topic.replace('/', '_')
    
    def _is_topic_excluded(self, topic: str) -> bool:
        """Check if a topic should be excluded based on excluded_topics config.
        Supports wildcards using * character.
        Returns True if the topic matches any exclusion pattern.
        """
        for excluded in self.excluded_topics:
            if self._topic_matches_pattern(topic, excluded):
                return True
                
        return False
    
    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if a topic matches a pattern with wildcard support.
        * matches any sequence of characters within a topic level
        """
        try:
            # If no wildcards, use exact matching and hierarchical matching
            if '*' not in pattern:
                # Check exact match
                if topic == pattern:
                    return True
                # Check if topic is a child of pattern (starts with pattern + '/')
                if topic.startswith(pattern + '/'):
                    return True
                return False
            
            # Split both topic and pattern by '/' to handle wildcards per level
            topic_parts = topic.split('/')
            pattern_parts = pattern.split('/')
            
            # For hierarchical matching, the pattern can match if:
            # 1. All pattern parts match the beginning of topic parts (exact match)
            # 2. Topic has more parts than pattern (hierarchical child match)
            
            # Check exact match first
            if self._match_parts_exact(topic_parts, pattern_parts):
                return True
                
            # Check hierarchical match - pattern matches prefix of topic
            if len(topic_parts) > len(pattern_parts):
                return self._match_parts_exact(topic_parts[:len(pattern_parts)], pattern_parts)
                
            return False
        except Exception as e:
            self.logger.error(f"Error matching topic '{topic}' against pattern '{pattern}': {e}")
            return False
    
    def _match_parts_exact(self, topic_parts: list, pattern_parts: list) -> bool:
        """Match topic parts against pattern parts exactly (same number of parts)"""
        if len(topic_parts) != len(pattern_parts):
            return False
            
        for i in range(len(pattern_parts)):
            if not self._match_single_part(topic_parts[i], pattern_parts[i]):
                return False
                
        return True
    
    def _match_single_part(self, topic_part: str, pattern_part: str) -> bool:
        """Match a single topic part against a pattern part with wildcard support"""
        if pattern_part == '*':
            return True
            
        if '*' not in pattern_part:
            return topic_part == pattern_part
            
        # Handle wildcards within the pattern part (like "temp*data")
        # Convert * to regex .* and escape other regex special chars
        regex_pattern = re.escape(pattern_part).replace('\\*', '.*')
        return re.match(f'^{regex_pattern}$', topic_part) is not None
    
    def _clean_excluded_topics_from_cache(self) -> None:
        """Remove any excluded topics from the existing cache"""
        if not self.excluded_topics:
            return
            
        with self.cache_lock:
            # Get list of element_ids to remove (can't modify dict while iterating)
            to_remove = []
            for element_id, topic_data in self.topic_cache.items():
                original_topic = topic_data['topic']
                if self._is_topic_excluded(original_topic):
                    to_remove.append(element_id)
            
            # Remove excluded topics from cache
            for element_id in to_remove:
                self.logger.info(f"Removing excluded topic from cache: {self.topic_cache[element_id]['topic']}")
                del self.topic_cache[element_id]
                
            if to_remove:
                self.logger.info(f"Cleaned {len(to_remove)} excluded topics from cache")