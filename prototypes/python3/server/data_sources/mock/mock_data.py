from datetime import datetime

# I3X API compliant mock data - Industrial Information Interface eXchange (RFC 001)
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
            "attributes": [
                {"name": "serialNumber", "dataType": "string"},
                {"name": "model", "dataType": "string"},
                {"name": "status", "dataType": "string"},
                {"name": "temperature", "dataType": "object", "engUnit": "CEL"},
                {"name": "powerConsumption", "dataType": "object", "engUnit": "KWH"}
            ]
        },
        {
            "elementId": "sensor-type-001",
            "name": "TemperatureSensor",
            "namespaceUri": "http://i3x.org/mfg/equipment",
            "attributes": [
                {"name": "value", "dataType": "number", "engUnit": "CEL"},
                {"name": "status", "dataType": "string"},
                {"name": "calibrationDate", "dataType": "string"}
            ]
        },
        {
            "elementId": "process-type-001",
            "name": "ManufacturingProcess",
            "namespaceUri": "http://i3x.org/mfg/process",
            "attributes": [
                {"name": "name", "dataType": "string"},
                {"name": "status", "dataType": "string"},
                {"name": "startTime", "dataType": "string"},
                {"name": "endTime", "dataType": "string"},
                {"name": "efficiency", "dataType": "number"}
            ]
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
            "relationships": {
                "controlledby": ["controller-001"],
                "connectedby": ["network-switch-001"],
                "suppliedby": ["conveyor-001"],
                "monitoredby": ["sensor-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "machine-002",
            "static": True,         
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
            "relationships": {
                "controlledby": ["controller-001"],
                "connectedby": ["network-switch-001"],
                "monitoredby": ["sensor-002"]
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
            "relationships": {
                "monitors": ["machine-001"]
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
            "relationships": {
                "monitoredby": ["sensor-003"],
                "controlledby": ["controller-002"],
                "suppliedby": ["material-feeder-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "sensor-002",
            "name": "PressureSensor-102",
            "typeId": "sensor-type-001",
            "parentId": None,  
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {                
                "value": 8.7,
                "engUnit": "BAR",
                "status": "active",
                "calibrationDate": "2025-02-10"
            },
            "relationships": {
                "monitors": ["machine-002"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "sensor-003",
            "name": "VibrationSensor-103",
            "typeId": "sensor-type-001",
            "parentId": None, 
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {                
                "value": 2.3,
                "engUnit": "MM/S",
                "status": "active",
                "calibrationDate": "2025-01-20"
            },
            "relationships": {
                "monitors": ["process-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "controller-001",
            "name": "PLC-Main-Controller",
            "typeId": "machine-type-001",  
            "parentId": None,  
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "PLC-12345",
                "model": "ControllerPro",
                "status": "active",                
                "temperature": {
                    "value": 35.2,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 0.8,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "controls": ["machine-001", "machine-002"],
                "connectedby": ["network-switch-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "controller-002",
            "name": "Process-Controller",
            "typeId": "machine-type-001",
            "parentId": None, 
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "PC-67890",
                "model": "ProcessPro",
                "status": "active",                
                "temperature": {
                    "value": 38.1,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 1.1,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "controls": ["process-001"],
                "connectedby": ["network-switch-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "network-switch-001",
            "name": "Industrial-Switch-Main",
            "typeId": "machine-type-001",
            "parentId": None,  
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "SW-11111",
                "model": "IndustrialSwitch24",
                "status": "active",                
                "temperature": {
                    "value": 28.5,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 0.3,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "connectsto": ["machine-001", "machine-002", "controller-001", "controller-002"],
                "connectedby": ["gateway-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "gateway-001",
            "name": "SCADA-Gateway",
            "typeId": "machine-type-001",
            "parentId": None, 
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "GW-22222",
                "model": "SCADAGateway",
                "status": "active",                
                "temperature": {
                    "value": 31.7,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 0.5,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "connectsto": ["network-switch-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "conveyor-001",
            "name": "Parts-Conveyor-A",
            "typeId": "machine-type-001",
            "parentId": None,  
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "CV-33333",
                "model": "ConveyorBelt200",
                "status": "running",                
                "temperature": {
                    "value": 22.3,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 2.1,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "suppliesto": ["machine-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        },
        {
            "elementId": "material-feeder-001",
            "name": "Raw-Material-Feeder",
            "typeId": "machine-type-001",
            "parentId": None, 
            "hasChildren": False,
            "namespaceUri": "http://i3x.org/mfg/equipment",            
            "attributes": {
                "serialNumber": "MF-44444",
                "model": "MaterialFeeder500",
                "status": "active",                
                "temperature": {
                    "value": 25.8,
                    "engUnit": "CEL"
                },
                "powerConsumption": {
                    "value": 1.5,
                    "engUnit": "KWH"
                }
            },
            "relationships": {
                "suppliesto": ["process-001"]
            },
            "timestamp": "2025-07-07T10:15:30Z"
        }
    ],
    "relationships": {
            "HasParent": "HasChildren",
            "HasChildren": "HasParent",
            "Monitors": "MonitoredBy",
            "Controls": "ControlledBy",
            "ConnectsTo": "ConnectedBy",
            "SuppliesTo": "SuppliedBy",
            "MonitoredBy": "Monitors",
            "ControlledBy": "Controls", 
            "ConnectedBy": "ConnectsTo",
            "SuppliedBy": "SuppliesTo"
    },
}
