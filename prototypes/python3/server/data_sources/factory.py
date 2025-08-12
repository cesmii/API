from typing import Dict, Any
from .data_interface import I3XDataSource
from .mock.mock_data_source import MockDataSource

class DataSourceFactory:
    """Factory for creating data source instances based on configuration"""
    
    @staticmethod
    def create_data_source(config: Dict[str, Any]) -> I3XDataSource:
        """Create a data source instance from configuration
        
        Args:
            config: Dictionary with 'type' and 'config' keys
            
        Returns:
            I3XDataSource instance
            
        Raises:
            ValueError: If data source type is not supported
        """
        data_source_type = config.get("type", "mock").lower()
        data_source_config = config.get("config", {})
        
        if data_source_type == "mock":
            return MockDataSource()
        else:
            raise ValueError(f"Unsupported data source type: {data_source_type}")
    
    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported data source types"""
        return ["mock"]