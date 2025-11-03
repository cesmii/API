import threading
import time
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Callable


class MockDataUpdater:
    """Handles random value generation for mock data source to simulate real-time updates"""

    def __init__(self, data_source):
        self.data_source = data_source
        self.running = False
        self.thread = None
        self.update_callback = None

    def start(self, update_callback: Optional[Callable] = None):
        """Start the background thread that generates random updates"""
        if self.running:
            return

        self.update_callback = update_callback
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the background update thread"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _update_loop(self):
        """Main loop that generates random updates"""
        while self.running:
            # Get all instances from the data source
            instances = self.data_source.get_all_instances()

            # Generate random updates for non-static instances
            for instance in instances:
                # Skip instances with "static" flag set to True
                if instance.get("static", False):
                    continue

                # Check if instance has a Values array
                values_array = instance.get("values")
                if (
                    not values_array
                    or not isinstance(values_array, list)
                    or len(values_array) == 0
                ):
                    continue

                # Get the most recent value (first element in array)
                current_value = values_array[0]

                # Make a copy to detect changes
                old_value = (
                    current_value.copy()
                    if isinstance(current_value, dict)
                    else current_value
                )

                # Randomize numeric values in the current value
                self.randomize_numeric_values(current_value)

                # Update timestamp (check for both "Timestamp" and "timestamp")
                timestamp_key = (
                    "Timestamp" if "Timestamp" in current_value else "timestamp"
                )
                current_value[timestamp_key] = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )

                # If callback is provided, notify about the update
                if self.update_callback and old_value != current_value:
                    self.update_callback(instance, current_value)

            time.sleep(1)  # Update every second

    def randomize_numeric_values(self, obj):
        """Simulate data changes by changing numeric values in the data"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (int, float)):
                    # Change numeric value randomly +/- up to 10%
                    variation = v * 0.1
                    new_val = v + random.uniform(-variation, variation)
                    # If original was int, convert back to int
                    obj[k] = int(new_val) if isinstance(v, int) else new_val
                elif isinstance(v, dict) or isinstance(v, list):
                    self.randomize_numeric_values(v)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (int, float)):
                    variation = item * 0.1
                    new_val = item + random.uniform(-variation, variation)
                    obj[i] = int(new_val) if isinstance(item, int) else new_val
                elif isinstance(item, dict) or isinstance(item, list):
                    self.randomize_numeric_values(item)
