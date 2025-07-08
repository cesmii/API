from datetime import datetime

# I3X API compliant mock data - Industrial Information Interface eXchange
I3X_DATA = {
    "namespaces": [
        {"uri": "http://i3x.org/mfg/equipment", "name": "Equipment"},
        {"uri": "http://i3x.org/mfg/process", "name": "Process"},
        {"uri": "http://i3x.org/mfg/quality", "name": "Quality"}
    ],
    "objectTypes": [
        {
            "elementId": "machine-type-001",
            "name": "CNCMachine",
            "namespaceUri": "http://i3x.org/mfg/equipment",
            "attributes": ["serialNumber", "model", "status", "temperature", "powerConsumption"]
        },
        {
            "elementId": "sensor-type-001",
            "name": "TemperatureSensor",
            "namespaceUri": "http://i3x.org/mfg/equipment",
            "attributes": ["value", "unit", "status", "calibrationDate"]
        },
        {
            "elementId": "process-type-001",
            "name": "ManufacturingProcess",
            "namespaceUri": "http://i3x.org/mfg/process",
            "attributes": ["name", "status", "startTime", "endTime", "efficiency"]
        }
    ],
    "instances": [
        {
            "elementId": "machine-001",
            "name": "CNC-101",
            "typeId": "machine-type-001",
            "parentId": "plant-001",
            "hasChildren": True,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "SN-45678",
                "model": "Model25",
                "status": "running",                
                "temperature": {
                    "value": 65.4,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 4.7,
                    "engUnit": "KWH"
                }
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "machine-002",
            "name": "CNC-102",
            "typeId": "machine-type-001",
            "parentId": "plant-001",
            "hasChildren": True,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "SN-45679",
                "model": "Model25",
                "status": "idle",                
                "temperature": {
                    "value": 42.1,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 1.2,
                    "engUnit": "KWH"
                }
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "sensor-001",
            "name": "TempSensor-101",
            "typeId": "sensor-type-001",
            "parentId": "machine-001",
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {                
                "value": 65.4,
                "engUnit": "CEL",
                "status": "active",
                "calibrationDate": "2025-01-15"
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "process-001",
            "name": "Part-XYZ-Production",
            "typeId": "process-type-001",            
            "parentId": None,
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/process",
            "attributes": {
                "name": "Part XYZ Production Run",                
                "status": "running",
                "startTime": "2025-07-07T08:00:00Z",
                "endTime": None,
                "efficiency": 92.5
            },
            "timestamp": "2025-07-07T10:15:30Z"
        }
    ],
    "relationships": {
        "hierarchical": ["HasParent", "HasChild"],
        "nonHierarchical": ["Monitors", "Controls", "ConnectsTo", "SuppliesTo"]
    }
}
