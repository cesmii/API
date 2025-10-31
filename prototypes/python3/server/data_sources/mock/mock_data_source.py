from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
from ..data_interface import I3XDataSource
from .mock_data import I3X_DATA
from .mock_updater import MockDataUpdater


class MockDataSource(I3XDataSource):
    """Mock data implementation of I3XDataSource"""

    def __init__(self):
        self.data = I3X_DATA
        self.updater = MockDataUpdater(self)
        self.update_callback = None

    def start(
        self, update_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> None:
        """Initialize mock data source and start background updates"""
        self.update_callback = update_callback
        self.updater.start(self.update_callback)

    def stop(self) -> None:
        """Stop mock data source and cleanup background updates"""
        self.updater.stop()

    def get_namespaces(self) -> List[Dict[str, Any]]:
        return self.data["namespaces"]

    def get_object_types(
        self, namespace_uri: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if namespace_uri:
            return [
                t
                for t in self.data["objectTypes"]
                if t["namespaceUri"] == namespace_uri
            ]
        return self.data["objectTypes"]

    def get_object_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        for obj_type in self.data["objectTypes"]:
            if obj_type["elementId"] == element_id:
                return obj_type
        return None

    def get_relationship_types(
        self, namespace_uri: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if namespace_uri:
            return [
                t
                for t in self.data["relationshipTypes"]
                if t["namespaceUri"] == namespace_uri
            ]
        return self.data["relationshipTypes"]


    def get_relationship_type_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        for obj_type in self.data["relationshipTypes"]:
            if obj_type["elementId"] == element_id:
                return obj_type
        return None

    def get_instances(self, type_id: Optional[str] = None) -> List[Dict[str, Any]]:
        instances = self.data["instances"]
        results = []
        if type_id:
            for instance in instances:
                if instance["typeId"] == type_id:
                    results.append(instance)
        else:
            results = instances

        # Filter out Values member from each instance before returning (unique to mock data)
        filtered_results = []
        for instance in results:
            filtered_instance = {k: v for k, v in instance.items() if k != "values"}
            filtered_results.append(filtered_instance)

        return filtered_results

    def get_instance_values_by_id(
        self,
        element_id: str,
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
    ):
        instance = self.get_instance_by_id(element_id, values=True)

        if not instance:
            return None

        # Get the Values array
        values_array = instance.get("values")

        # If no Values or Values is not a list, return as is
        if not values_array or not isinstance(values_array, list):
            return None

        returned_value = None

        # Filter based on time range
        if startTime and endTime:
            # Parse time strings to datetime objects for comparison
            start_dt = datetime.fromisoformat(startTime.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(endTime.replace("Z", "+00:00"))

            # Filter Values array to only include items within time range
            filtered_values = []
            for value_item in values_array:
                # Check for both "timestamp" and "Timestamp" (case-insensitive)
                timestamp_key = None
                for key in ["timestamp", "Timestamp"]:
                    if key in value_item:
                        timestamp_key = key
                        break

                if timestamp_key:
                    value_dt = datetime.fromisoformat(
                        value_item[timestamp_key].replace("Z", "+00:00")
                    )
                    if start_dt <= value_dt <= end_dt:
                        filtered_values.append(value_item)

            returned_value = filtered_values
        else:
            # No time range specified - return only the most recent value based on timestamp
            most_recent = None
            most_recent_dt = None

            for value_item in values_array:
                # Check for both "timestamp" and "Timestamp" (case-insensitive)
                timestamp_key = None
                for key in ["timestamp", "Timestamp"]:
                    if key in value_item:
                        timestamp_key = key
                        break

                if timestamp_key:
                    value_dt = datetime.fromisoformat(
                        value_item[timestamp_key].replace("Z", "+00:00")
                    )
                    if most_recent_dt is None or value_dt > most_recent_dt:
                        most_recent_dt = value_dt
                        most_recent = value_item

            returned_value = most_recent

        return returned_value

    def get_instance_by_id(
        self, element_id: str, values: bool = False
    ) -> Optional[Dict[str, Any]]:
        for instance in self.data["instances"]:
            if instance["elementId"] == element_id:
                if values:
                    # Return instance with Values included
                    return instance
                else:
                    # Filter out Values member from each instance before returning (unique to mock data)
                    filtered_instance = {
                        k: v for k, v in instance.items() if k != "values"
                    }
                    return filtered_instance
        return None

    def get_related_instances(
        self, element_id: str, relationship_type: str
    ) -> List[Dict[str, Any]]:
        related_objects = []

        # Get the source instance directly from data (not filtered) to preserve relationships
        source_instance = None
        for instance in self.data["instances"]:
            if instance["elementId"] == element_id:
                source_instance = instance
                break

        if not source_instance:
            return related_objects

        # Check if instance has explicit relationship metadata
        relationships_metadata = source_instance.get("relationships", {})

        # Look for the relationship type (case-insensitive match)
        matching_key = None
        for key in relationships_metadata.keys():
            if key.lower() == relationship_type.lower():
                matching_key = key
                break

        if matching_key:
            # Return instances based on explicit relationship declarations
            related_ids = relationships_metadata[matching_key]
            if isinstance(related_ids, list):
                # Get instances directly from data for list of IDs
                related_objects = [
                    i for i in self.data["instances"] if i["elementId"] in related_ids
                ]
            else:
                # Handle single ID case - get directly from data
                for instance in self.data["instances"]:
                    if instance["elementId"] == related_ids:
                        related_objects = [instance]
                        break
        # Fallback: Handle non-hierarchical relationships dynamically
        else:
            related_objects = self._process_non_hierarchical_relations(
                element_id, relationship_type.lower()
            )

        # Filter out Values member from each instance before returning (unique to mock data)
        filtered_results = []
        for instance in related_objects:
            filtered_instance = {k: v for k, v in instance.items() if k != "values"}
            filtered_results.append(filtered_instance)

        return filtered_results

    def _process_non_hierarchical_relations(
        self, element_id: str, relationship_type: str
    ) -> List[Dict[str, Any]]:
        """Fallback for dynamically determining relationships not found in metadata"""
        # This method can be extended in the future for semantic pattern matching
        # For now, return empty list since relationships should be explicit
        return []

    def update_instance_value(
        self, element_id: str, value: Any
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone

        # Note this is a hack for now as the code below can handle multiple updates but for now we just want one
        element_ids = [element_id]
        values = [value]

        results = []
        for element_id, value in zip(element_ids, values):
            instance = self.get_instance_by_id(element_id, values=True)
            if not instance:
                results.append(
                    {
                        "elementId": element_id,
                        "success": False,
                        "message": "Element not found",
                    }
                )
                continue

            try:
                # Validate the write schema matches the instance schema
                value_schema = self._get_schema(value)
                instance_schema = self._get_schema(instance["values"][0])

                print(f"Value schema: {value_schema}")
                print(f"Instance schema: {instance_schema}")

                if value_schema != instance_schema:
                    raise Exception("Value schema does not match instance schema")

                instance["values"][0] = value
                instance["timestamp"] = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )

                results.append(
                    {
                        "elementId": element_id,
                        "success": True,
                        "message": "Updated successfully",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "elementId": element_id,
                        "success": False,
                        "message": f"Update failed: {str(e)}",
                    }
                )

        return results[0]

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
        return self.data["instances"]
