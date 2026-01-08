"""
CNC Mock Data Source Package

Provides a simulated CNC machine data source based on the CESMII CNC profile
(OPC UA NodeSet2 information model).
"""
from .cnc_data_source import CNCDataSource

__all__ = ["CNCDataSource"]
