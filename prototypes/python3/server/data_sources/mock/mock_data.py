from datetime import datetime

# TODOs and Considerations
# - Looking at the way the instances are defined, the isa types are not really following their schema in the mock data. 
# - Consider representing relationships in json schema
# - Find other spots where types can be references instead of re-defined
# - Consider using full URI to refer to namespaces and their types to ensure uniqueness and ease of use with JSON Schema
# - Revisit how to handle measurements and other types where there may be many values for many sources 

# I3X API compliant mock data - Industrial Information Interface eXchange (RFC 001)
I3X_DATA = {
    "namespaces": [
        {"uri": "https://cesmii.org/i3x", "displayName": "I3X"},
        {"uri": "https://isa.org/isa95", "displayName": "ISA95"},
        {"uri": "https://abelara.com/equipment", "displayName": "Abelara Equipment"},
        {"uri": "https://thinkiq.com/equipment", "displayName": "ThinkIQ Equipment"},
        {
            "uri": "http://opcfoundation.org/UA/Machinery",
            "displayName": "OPC UA for Machinery",
        },
    ],
    "objectTypes": [
        {
            "elementId": "enterprise-type",
            "displayName": "Enterprise",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Schemas/isa95/enterprise-type.json",
        },
        {
            "elementId": "site-type",
            "displayName": "Site",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Schemas/isa95/site-type.json",
        },
        {
            "elementId": "area-type",
            "displayName": "Area",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Schemas/isa95/area-type.json",
        },
        {
            "elementId": "work-center-type",
            "displayName": "Work-Center",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Schemas/isa95/work-center-type.json",
        },
        {
            "elementId": "work-unit-type",
            "displayName": "Work-Unit",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Schemas/isa95/work-unit-type.json",
        },
        {
            "elementId": "state-type",
            "displayName": "State",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/state-type.json",
        },
        {
            "elementId": "alert-type",
            "displayName": "Alert",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/alert-type.json",
        },
        {
            "elementId": "product-type",
            "displayName": "Product",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/product-type.json",
        },
        {
            "elementId": "production-type",
            "displayName": "Production",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/production-type.json",
        },
        {
            "elementId": "measurements-type",
            "displayName": "Measurements",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/measurements-type.json",
        },
        {
            "elementId": "measurement-type",
            "displayName": "Measurement",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/measurement-type.json",
        },
        {
            "elementId": "count-type",
            "displayName": "Count",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/count-type.json",
        },
        {
            "elementId": "kpi-type",
            "displayName": "KPI",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/kpi-type.json",
        },
        {
            "elementId": "measurement-type",
            "displayName": "Measurement",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Schemas/abelara/measurement-type.json",
        },
        {
            "elementId": "sensor-type",
            "displayName": "Sensor",
            "namespaceUri": "https://thinkiq.com/equipment",
            "schema": "Schemas/thinkiq/sensor-type.json",
        },
        {
            "elementId": "tank-type",
            "displayName": "Tank",
            "namespaceUri": "https://cesmii.org/i3x",
            "schema": "Schemas/i3x/tank-type.json",
        },
        {
            "elementId": "pump-type",
            "displayName": "Pump",
            "namespaceUri": "https://cesmii.org/i3x",
            "schema": "Schemas/i3x/pump-type.json",
        },        
    ],
    "instances": [
        {
            "elementId": "pump-999",
            "displayName": "Pump 999",
            "typeId": "pump-type",
            "namespaceUri": "https://cesmii.org/i3x",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-enterprise"],
            },
            "values": [
                {
                    "alert": {
                        "timestamp": "2025-10-29T18:24:50.802109+00:00",
                        "severity": 3,
                        "code": "TEMP_ALARM",
                        "message": "Pump bearing temperature above alert threshold",
                        "metadata": {
                            "source": "monitoring-system",
                            "uri": "opc://plc1/DB1.DBD4",
                            "asset": {
                                "id": 101,
                                "name": "Pump-101",
                                "description": "Centrifugal water pump for cooling system",
                            },
                            "acknowledgment": {
                                "acknowledged": False,
                                "acknowledgedBy": None,
                                "acknowledgedAt": None,
                            },
                            "additionalInfo": {
                                "temperature": 106.1,
                                "warningThreshold": 75.0,
                                "alarmThreshold": 85.0,
                                "sensorLocation": "Drive End Bearing",
                                "trend": "Rising",
                                "timeInAlarm": 23,
                                "recommendedAction": "Check alignment",
                                "priority": "Low",
                            },
                        },
                    },
                    "state": {
                        "timestamp": "2025-10-29T18:20:44.779036+00:00",
                        "description": "Pump is in maintenance",
                        "color": "#800080",
                        "type": {
                            "id": 5,
                            "name": "Maintenance",
                            "description": "Equipment under maintenance",
                        },
                        "metadata": {
                            "source": "plc-controller",
                            "uri": "opc://plc1/DB1.DBW0",
                            "asset": {
                                "id": 101,
                                "name": "Pump-101",
                                "description": "Centrifugal water pump for cooling system",
                            },
                            "previousState": {
                                "id": 2,
                                "name": "Full",
                                "description": "Tank is full",
                                "color": "#228B22",
                                "type": {
                                    "id": 2,
                                    "name": "Full",
                                    "description": "Tank is full",
                                },
                            },
                            "additionalInfo": {
                                "runTime": 1167,
                                "lastFillTime": "2025-10-29T18:42:41.516272+00:00",
                                "mode": "AUTO",
                                "operator": "Jane Doe"                                
                            },                            

                        },
                    },
                    "product": {
                        "timestamp": "2025-10-29T18:27:55.457173+00:00",
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water for heat exchange systems",
                        "idealCycleTime": 3600,
                        "tolerance": 0.05,
                        "unit": "m\u00b3/h",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                        "metadata": {
                            "source": "product-management",
                            "uri": "product://cooling-water",
                            "asset": {
                                "id": 101,
                                "name": "Pump-101",
                                "description": "Centrifugal water pump for cooling system",
                            },
                            "additionalInfo": {
                                "specifications": {
                                    "temperature": "15-25\u00b0C",
                                    "pressure": "3-8 bar",
                                    "quality": "Process Grade",
                                    "chlorinated": True,
                                },
                                "regulatoryCompliance": [
                                    "ISO 14001",
                                    "Water Quality Standards",
                                ],
                            },
                        },
                    },          
                    "production": {
                        "timestamp": "2025-10-29T18:29:53.368598+00:00",
                        "start_ts": "2025-10-29T18:29:53.368607+00:00",
                        "end_ts": None,
                        "counts": [
                            {
                                "type": {
                                    "id": 1,
                                    "name": "Water Delivered",
                                    "description": "Total water delivered to cooling system",
                                    "unit": "m\u00b3",
                                },
                                "value": 320,
                                "timestamp": "2025-10-29T18:29:53.368610+00:00",
                            },
                            {
                                "type": {
                                    "id": 2,
                                    "name": "Runtime Hours",
                                    "description": "Total pump runtime hours",
                                    "unit": "hours",
                                },
                                "value": 6.9,
                                "timestamp": "2025-10-29T18:29:53.368615+00:00",
                            },
                        ],
                        "metadata": {
                            "source": "production-tracker",
                            "uri": "production://cooling-system-2024-009",
                            "asset": {
                                "id": 101,
                                "name": "Pump-101",
                                "description": "Centrifugal water pump for cooling system",
                            },
                            "product": {
                                "id": 1,
                                "name": "Cooling Water",
                                "description": "Process cooling water for heat exchange systems",
                                "idealCycleTime": 3600,
                                "tolerance": 0.05,
                                "unit": "m\u00b3/h",
                                "family": {
                                    "id": 1,
                                    "name": "Utilities",
                                    "description": "Utility products and services",
                                },
                            },
                            "additionalInfo": {
                                "shift": "Weekend",
                                "operator": "Bob Wilson",
                                "demandLevel": "High",
                                "systemEfficiency": 96.6,
                                "energyConsumption": 32.3,
                                "qualityScore": 101.1,
                                "plannedProduction": 350,
                                "actualProduction": 320,
                                "efficiency": 91.4,
                            },
                        },
                    },
                    "measurements":[
                        {
                            "timestamp": "2025-10-28T18:32:47.673157+00:00",
                            "type": {
                                "id": 1,
                                "name": "Bearing Temperature",
                                "description": "Precision bearing temperature measurement",
                            },
                            "value": 70.34,
                            "unit": "\u00b0C",
                            "target": 70.0,
                            "tolerance": 10.5,
                            "inTolerance": True,
                            "metadata": {
                                "source": "precision-maintenance",
                                "uri": "maintenance://pump-101/bearing-temperature",
                                "asset": {
                                    "id": 101,
                                    "name": "Pump-101",
                                    "description": "Centrifugal water pump for cooling system",
                                },
                                "additionalInfo": {
                                    "technician": "John Smith",
                                    "measurementMethod": "Oil Sampling",
                                    "equipmentUsed": "Fluke Ti480",
                                    "measurementDate": "2025-10-29T18:32:47.673173+00:00",
                                    "nextMeasurementDue": "2024-06-15",
                                    "trend": "Deteriorating",
                                    "measurementLocation": "Drive End Bearing",
                                },
                            },
                            "product": {
                                "id": 1,
                                "name": "Cooling Water",
                                "description": "Process cooling water",
                                "family": {
                                    "id": 1,
                                    "name": "Utilities",
                                    "description": "Utility products and services",
                                },
                            },
                            "productionContext": {
                                "batchId": "MAINT-2024-979",
                                "processStep": "Precision Maintenance",
                                "demand": "Emergency",
                            },
                        },
                        {
                            "timestamp": "2025-10-29T18:34:55.885390+00:00",
                            "type": {
                                "id": 2,
                                "name": "Vibration Analysis",
                                "description": "Precision vibration measurement",
                            },
                            "value": 1.36,
                            "unit": "mm/s",
                            "target": 1.2,
                            "tolerance": 0.18,
                            "inTolerance": False,
                            "metadata": {
                                "source": "precision-maintenance",
                                "uri": "maintenance://pump-101/vibration-analysis",
                                "asset": {
                                    "id": 101,
                                    "name": "Pump-101",
                                    "description": "Centrifugal water pump for cooling system",
                                },
                                "additionalInfo": {
                                    "technician": "Mike Johnson",
                                    "measurementMethod": "Laser Alignment",
                                    "equipmentUsed": "Spectro Scientific",
                                    "measurementDate": "2025-10-29T18:34:55.885397+00:00",
                                    "nextMeasurementDue": "2024-06-15",
                                    "trend": "Deteriorating",
                                    "measurementLocation": "Drive End",
                                },
                            },
                            "product": {
                                "id": 1,
                                "name": "Cooling Water",
                                "description": "Process cooling water",
                                "family": {
                                    "id": 1,
                                    "name": "Utilities",
                                    "description": "Utility products and services",
                                },
                            },
                            "productionContext": {
                                "batchId": "MAINT-2024-438",
                                "processStep": "Precision Maintenance",
                                "demand": "Condition Based",
                            },
                        },
                        {
                            "timestamp": "2025-10-29T18:35:42.019884+00:00",
                            "type": {
                                "id": 3,
                                "name": "Oil Analysis",
                                "description": "Oil quality measurement",
                            },
                            "value": 12.41,
                            "unit": "mg/kg",
                            "target": 8.0,
                            "tolerance": 1.2,
                            "inTolerance": False,
                            "metadata": {
                                "source": "precision-maintenance",
                                "uri": "maintenance://pump-101/oil-analysis",
                                "asset": {
                                    "id": 101,
                                    "name": "Pump-101",
                                    "description": "Centrifugal water pump for cooling system",
                                },
                                "additionalInfo": {
                                    "technician": "Jane Doe",
                                    "measurementMethod": "Infrared Thermography",
                                    "equipmentUsed": "Fluke 1507",
                                    "measurementDate": "2025-10-29T18:35:42.019891+00:00",
                                    "nextMeasurementDue": "2024-06-15",
                                    "trend": "Deteriorating",
                                    "measurementLocation": "Oil Reservoir",
                                },
                            },
                            "product": {
                                "id": 1,
                                "name": "Cooling Water",
                                "description": "Process cooling water",
                                "family": {
                                    "id": 1,
                                    "name": "Utilities",
                                    "description": "Utility products and services",
                                },
                            },
                            "productionContext": {
                                "batchId": "MAINT-2024-852",
                                "processStep": "Precision Maintenance",
                                "demand": "Emergency",
                            },
                        },                    
                    ],
                }
            ]            
        },
        {
            "elementId": "tank-000",
            "displayName": "Tank 000",
            "typeId": "tank-type",
            "namespaceUri": "https://cesmii.org/i3x",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system"],
                "SuppliedBy": ["pump-101"],
                "MonitoredBy": ["sensor-001"]
            },
            "values": [
                {
                    "machineId": {
                        "id": 200,
                        "name": "Tank-000",
                        "description": "Storage tank for process feed"
                    },
                    "state": {
                        "timestamp": "2025-11-05T12:00:00Z",
                        "description": "Tank in normal operation",
                        "color": "#228B22",
                        "type": {
                            "id": 1,
                            "name": "Full",
                            "description": "Tank is full"
                        },
                        "metadata": {
                            "source": "plc-controller",
                            "uri": "opc://plc1/DB1.DBW20",
                            "asset": {
                                "id": 200,
                                "name": "Tank-000",
                                "description": "Storage tank for process feed"
                            },
                            "previousState": {
                                "id": 3,
                                "name": "Filling",
                                "description": "Tank is filling",
                                "color": "#00BFFF",
                                "type": {
                                    "id": 3,
                                    "name": "Filling",
                                    "description": "Tank is being filled"
                                }
                            },
                            "additionalInfo": {
                                "runTime": 1024,
                                "lastFillTime": "2025-11-05T08:30:00Z",
                                "mode": "AUTO",
                                "operator": "Operator A"
                            }
                        }
                    },
                    "alert": {
                        "timestamp": "2025-11-05T11:50:00Z",
                        "severity": 1,
                        "code": "LEVEL_WARNING",
                        "message": "Tank level approaching high threshold",
                        "metadata": {
                            "source": "monitoring-system",
                            "uri": "opc://plc1/DB1.DBD50",
                            "asset": {
                                "id": 200,
                                "name": "Tank-000",
                                "description": "Storage tank for process feed"
                            },
                            "acknowledgment": {
                                "acknowledged": False,
                                "acknowledgedBy": None,
                                "acknowledgedAt": None
                            },
                            "additionalInfo": {
                                    "temperature": 22.4,
                                    "warningThreshold": 4.5,
                                    "alarmThreshold": 5.0,
                                    "waterLevel": 4.6,
                                    "minThreshold": 1.0,
                                    "maxThreshold": 5.0,
                                    "sensorLocation": "Top Center",
                                    "trend": "Rising",
                                    "timeInAlarm": 3,
                                    "recommendedAction": "Monitor level",
                                    "priority": "Medium"
                                }
                        }
                    }
                }
            ]
        },
        {
            "elementId": "cesmii-enterprise",
            "displayName": "CESMII",
            "typeId": "enterprise-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasChildren": ["cesmii-plant-1"],
            },
        },
        {
            "elementId": "cesmii-plant-1",
            "displayName": "CESMII Plant 1",
            "typeId": "site-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-enterprise"],
                "HasChildren": ["cesmii-plant-1-utilities"],
            },
        },
        {
            "elementId": "cesmii-plant-1-utilities",
            "displayName": "Utilities",
            "typeId": "area-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-plant-1"],
                "HasChildren": ["cesmii-plant-1-utilities-water-system"],
            },
        },
        {
            "elementId": "cesmii-plant-1-utilities-water-system",
            "displayName": "Water System",
            "typeId": "work-center-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities"],
                "HasChildren": ["cesmii-plant-1-utilities-water-system-pump-station"],
            },
        },
        {
            "elementId": "cesmii-plant-1-utilities-water-system-pump-station",
            "displayName": "Pump Station",
            "typeId": "work-center-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system"],
                "HasChildren": [
                    "cesmii-plant-1-utilities-water-system-pump-station-pump-101"
                ],
            },
        },
        {
            "elementId": "cesmii-plant-1-utilities-water-system-pump-station-pump-101",
            "displayName": "pump-101",
            "typeId": "work-unit-type",
            "namespaceUri": "https://isa.org/isa95",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-station"],
                "HasChildren": [
                    "pump-101-state",
                    "pump-101-alert",
                    "pump-101-product",
                    "pump-101-production",
                    "pump-101-measurements",
                ],
                "SuppliesTo": ["tank-201"],
            },
        },
        {
            "elementId": "pump-101-state",
            "displayName": "pump-101 State",
            "typeId": "state-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-101"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:20:44.779036+00:00",
                    "description": "Pump is in maintenance",
                    "color": "#800080",
                    "type": {
                        "id": 5,
                        "name": "Maintenance",
                        "description": "Equipment under maintenance",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW0",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "previousState": {
                            "id": 2,
                            "name": "Full",
                            "description": "Previously full",
                            "color": "#228B22",
                            "type": {
                                "id": 2,
                                "name": "Full",
                                "description": "Previously full"
                            }
                        },
                        "additionalInfo": {
                            "runTime": 1200,
                            "lastFillTime": "2025-10-29T07:00:00Z",
                            "mode": "AUTO",
                            "operator": "Operator B"
                        },
                    },
                },
                {
                    "timestamp": "2025-10-28T18:20:44.779036+00:00",
                    "description": "Pump is in operation",
                    "color": "#00FF00",
                    "type": {
                        "id": 1,
                        "name": "Operating",
                        "description": "Equipment operating normally",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW0",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "previousState": {
                            "id": 1,
                            "name": "Operating",
                            "description": "Previously operating",
                            "color": "#00FF00",
                            "type": {
                                "id": 1,
                                "name": "Operating",
                                "description": "Previously operating"
                            }
                        },
                        "additionalInfo": {
                            "runTime": 800,
                            "lastFillTime": "2025-10-28T06:30:00Z",
                            "mode": "AUTO",
                            "operator": "Operator C"
                        },
                    },
                },
                {
                    "timestamp": "2025-10-27T18:20:44.779036+00:00",
                    "description": "Pump is in operation",
                    "color": "#FFFF00",
                    "type": {
                        "id": 1,
                        "name": "Starved",
                        "description": "Equipment starved",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW0",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "previousState": {
                            "id": 3,
                            "name": "Starved",
                            "description": "Previously starved",
                            "color": "#FFD700",
                            "type": {
                                "id": 3,
                                "name": "Starved",
                                "description": "Previously starved"
                            }
                        },
                        "additionalInfo": {
                            "runTime": 400,
                            "lastFillTime": "2025-10-27T02:15:00Z",
                            "mode": "MANUAL",
                            "operator": "Operator D"
                        },
                    },
                },
            ],
        },
        {
            "elementId": "pump-101-alert",
            "displayName": "pump-101 Alert",
            "typeId": "alert-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-101"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:24:50.802109+00:00",
                    "severity": 3,
                    "code": "TEMP_ALARM",
                    "message": "Pump bearing temperature above alert threshold",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD4",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "acknowledgment": {
                            "acknowledged": False,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 106.1,
                            "warningThreshold": 75.0,
                            "alarmThreshold": 85.0,
                            "sensorLocation": "Drive End Bearing",
                            "trend": "Rising",
                            "timeInAlarm": 23,
                            "recommendedAction": "Check alignment",
                            "priority": "Low",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-29T18:26:07.704923+00:00",
                    "severity": 2,
                    "code": "TEMP_HIGH",
                    "message": "Pump bearing temperature exceeds warning threshold",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD4",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "acknowledgment": {
                            "acknowledged": False,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 78.7,
                            "warningThreshold": 75.0,
                            "alarmThreshold": 85.0,
                            "sensorLocation": "Drive End Bearing",
                            "trend": "Stable",
                            "timeInAlarm": 12,
                            "recommendedAction": "Reduce load",
                            "priority": "Medium",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-29T18:23:28.764138+00:00",
                    "severity": 1,
                    "code": "MAINT_DUE",
                    "message": "Pump maintenance due within 100 hours",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD4",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "acknowledgment": {
                            "acknowledged": False,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 77.0,
                            "warningThreshold": 75.0,
                            "alarmThreshold": 85.0,
                            "sensorLocation": "Drive End Bearing",
                            "trend": "Stable",
                            "timeInAlarm": 21,
                            "recommendedAction": "Check alignment",
                            "priority": "Critical",
                        },
                    },
                },
            ],
        },
        {
            "elementId": "pump-101-product",
            "displayName": "pump-101 Product",
            "typeId": "product-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-101"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:27:55.457173+00:00",
                    "id": 1,
                    "name": "Cooling Water",
                    "description": "Process cooling water for heat exchange systems",
                    "idealCycleTime": 3600,
                    "tolerance": 0.05,
                    "unit": "m\u00b3/h",
                    "family": {
                        "id": 1,
                        "name": "Utilities",
                        "description": "Utility products and services",
                    },
                    "metadata": {
                        "source": "product-management",
                        "uri": "product://cooling-water",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "specifications": {
                                "temperature": "15-25\u00b0C",
                                "pressure": "3-8 bar",
                                "quality": "Process Grade",
                                "chlorinated": True,
                            },
                            "regulatoryCompliance": [
                                "ISO 14001",
                                "Water Quality Standards",
                            ],
                        },
                    },
                }
            ],
        },
        {
            "elementId": "pump-101-production",
            "displayName": "pump-101 Production",
            "typeId": "production-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-101"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:29:53.368598+00:00",
                    "start_ts": "2025-10-29T18:29:53.368607+00:00",
                    "end_ts": None,
                    "counts": [
                        {
                            "type": {
                                "id": 1,
                                "name": "Water Delivered",
                                "description": "Total water delivered to cooling system",
                                "unit": "m\u00b3",
                            },
                            "value": 320,
                            "timestamp": "2025-10-29T18:29:53.368610+00:00",
                        },
                        {
                            "type": {
                                "id": 2,
                                "name": "Runtime Hours",
                                "description": "Total pump runtime hours",
                                "unit": "hours",
                            },
                            "value": 6.9,
                            "timestamp": "2025-10-29T18:29:53.368615+00:00",
                        },
                    ],
                    "metadata": {
                        "source": "production-tracker",
                        "uri": "production://cooling-system-2024-009",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "product": {
                            "id": 1,
                            "name": "Cooling Water",
                            "description": "Process cooling water for heat exchange systems",
                            "idealCycleTime": 3600,
                            "tolerance": 0.05,
                            "unit": "m\u00b3/h",
                            "family": {
                                "id": 1,
                                "name": "Utilities",
                                "description": "Utility products and services",
                            },
                        },
                        "additionalInfo": {
                            "shift": "Weekend",
                            "operator": "Bob Wilson",
                            "demandLevel": "High",
                            "systemEfficiency": 96.6,
                            "energyConsumption": 32.3,
                            "qualityScore": 101.1,
                            "plannedProduction": 350,
                            "actualProduction": 320,
                            "efficiency": 91.4,
                        },
                    },
                }
            ],
        },
        {
            "elementId": "pump-101-measurements",
            "displayName": "pump-101 Measurements",
            "typeId": "measurements-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": True,
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system-pump-101"],
                "HasChildren": [
                    "pump-101-measurements-bearing-temperature",
                    "pump-101-measurements-vibration-analysis",
                    "pump-101-measurements-oil-analysis",
                ],
            },
        },
        {
            "elementId": "pump-101-bearing-temperature",
            "displayName": "pump-101 Bearing Temperature",
            "typeId": "measurement-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["pump-101-measurements"],
            },
            "values": [
                {
                    "timestamp": "2025-10-28T18:32:47.673157+00:00",
                    "type": {
                        "id": 1,
                        "name": "Bearing Temperature",
                        "description": "Precision bearing temperature measurement",
                    },
                    "value": 70.34,
                    "unit": "\u00b0C",
                    "target": 70.0,
                    "tolerance": 10.5,
                    "inTolerance": True,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/bearing-temperature",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "John Smith",
                            "measurementMethod": "Oil Sampling",
                            "equipmentUsed": "Fluke Ti480",
                            "measurementDate": "2025-10-29T18:32:47.673173+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Drive End Bearing",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-979",
                        "processStep": "Precision Maintenance",
                        "demand": "Emergency",
                    },
                },
                {
                    "timestamp": "2025-10-29T18:32:47.673157+00:00",
                    "type": {
                        "id": 1,
                        "name": "Bearing Temperature",
                        "description": "Precision bearing temperature measurement",
                    },
                    "value": 71.79,
                    "unit": "\u00b0C",
                    "target": 70.0,
                    "tolerance": 10.5,
                    "inTolerance": True,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/bearing-temperature",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "John Smith",
                            "measurementMethod": "Oil Sampling",
                            "equipmentUsed": "Fluke Ti480",
                            "measurementDate": "2025-10-29T18:32:47.673173+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Drive End Bearing",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-979",
                        "processStep": "Precision Maintenance",
                        "demand": "Emergency",
                    },
                },
            ],
        },
        {
            "elementId": "pump-101-vibration-analysis",
            "displayName": "pump-101 Vibration Analysis",
            "typeId": "measurement-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["pump-101-measurements"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:34:55.885390+00:00",
                    "type": {
                        "id": 2,
                        "name": "Vibration Analysis",
                        "description": "Precision vibration measurement",
                    },
                    "value": 1.36,
                    "unit": "mm/s",
                    "target": 1.2,
                    "tolerance": 0.18,
                    "inTolerance": False,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/vibration-analysis",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "Mike Johnson",
                            "measurementMethod": "Laser Alignment",
                            "equipmentUsed": "Spectro Scientific",
                            "measurementDate": "2025-10-29T18:34:55.885397+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Drive End",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-438",
                        "processStep": "Precision Maintenance",
                        "demand": "Condition Based",
                    },
                },
                {
                    "timestamp": "2025-10-28T18:34:55.885390+00:00",
                    "type": {
                        "id": 2,
                        "name": "Vibration Analysis",
                        "description": "Precision vibration measurement",
                    },
                    "value": 1.75,
                    "unit": "mm/s",
                    "target": 1.2,
                    "tolerance": 0.18,
                    "inTolerance": False,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/vibration-analysis",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "Mike Johnson",
                            "measurementMethod": "Laser Alignment",
                            "equipmentUsed": "Spectro Scientific",
                            "measurementDate": "2025-10-29T18:34:55.885397+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Drive End",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-438",
                        "processStep": "Precision Maintenance",
                        "demand": "Condition Based",
                    },
                },
            ],
            "timestamp": "2025-10-29T10:15:30Z",
        },
        {
            "elementId": "pump-101-oil-analysis",
            "displayName": "pump-101 Oil Analysis",
            "typeId": "measurement-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["pump-101-measurements"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:35:42.019884+00:00",
                    "type": {
                        "id": 3,
                        "name": "Oil Analysis",
                        "description": "Oil quality measurement",
                    },
                    "value": 12.41,
                    "unit": "mg/kg",
                    "target": 8.0,
                    "tolerance": 1.2,
                    "inTolerance": False,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/oil-analysis",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "Jane Doe",
                            "measurementMethod": "Infrared Thermography",
                            "equipmentUsed": "Fluke 1507",
                            "measurementDate": "2025-10-29T18:35:42.019891+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Oil Reservoir",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-852",
                        "processStep": "Precision Maintenance",
                        "demand": "Emergency",
                    },
                },
                {
                    "timestamp": "2025-10-28T18:35:42.019884+00:00",
                    "type": {
                        "id": 3,
                        "name": "Oil Analysis",
                        "description": "Oil quality measurement",
                    },
                    "value": 9.35,
                    "unit": "mg/kg",
                    "target": 8.0,
                    "tolerance": 1.2,
                    "inTolerance": False,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/oil-analysis",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "Jane Doe",
                            "measurementMethod": "Infrared Thermography",
                            "equipmentUsed": "Fluke 1507",
                            "measurementDate": "2025-10-29T18:35:42.019891+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Oil Reservoir",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-852",
                        "processStep": "Precision Maintenance",
                        "demand": "Emergency",
                    },
                },
                {
                    "timestamp": "2025-10-27T18:35:42.019884+00:00",
                    "type": {
                        "id": 3,
                        "name": "Oil Analysis",
                        "description": "Oil quality measurement",
                    },
                    "value": 11.77,
                    "unit": "mg/kg",
                    "target": 8.0,
                    "tolerance": 1.2,
                    "inTolerance": False,
                    "metadata": {
                        "source": "precision-maintenance",
                        "uri": "maintenance://pump-101/oil-analysis",
                        "asset": {
                            "id": 101,
                            "name": "Pump-101",
                            "description": "Centrifugal water pump for cooling system",
                        },
                        "additionalInfo": {
                            "technician": "Jane Doe",
                            "measurementMethod": "Infrared Thermography",
                            "equipmentUsed": "Fluke 1507",
                            "measurementDate": "2025-10-29T18:35:42.019891+00:00",
                            "nextMeasurementDue": "2024-06-15",
                            "trend": "Deteriorating",
                            "measurementLocation": "Oil Reservoir",
                        },
                    },
                    "product": {
                        "id": 1,
                        "name": "Cooling Water",
                        "description": "Process cooling water",
                        "family": {
                            "id": 1,
                            "name": "Utilities",
                            "description": "Utility products and services",
                        },
                    },
                    "productionContext": {
                        "batchId": "MAINT-2024-852",
                        "processStep": "Precision Maintenance",
                        "demand": "Emergency",
                    },
                },
            ],
        },
        {
            "elementId": "tank-201",
            "displayName": "tank-201",
            "typeId": "work-unit-type",
            "hasChildren": True,
            "namespaceUri": "https://isa.org/isa95",
            "relationships": {
                "HasParent": ["cesmii-plant-1-utilities-water-system"],
                "HasChildren": ["tank-201-machine-id", "tank-201-state"],
                "SuppliedBy": "pump-101",
                "MonitoredBy": "sensor-001",
            },
        },
        {
            "elementId": "tank-201-state",
            "displayName": "tank-201 State",
            "typeId": "state-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["tank-201"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:42:41.516253+00:00",
                    "description": "Tank is maintenance",
                    "color": "#800080",
                    "type": {
                        "id": 5,
                        "name": "Maintenance",
                        "description": "Tank under maintenance",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW10",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "previousState": {
                            "id": 2,
                            "name": "Full",
                            "description": "Tank is full",
                            "color": "#228B22",
                            "type": {
                                "id": 2,
                                "name": "Full",
                                "description": "Tank is full",
                            },
                        },
                        "additionalInfo": {
                            "runTime": 562,
                            "lastFillTime": "2025-10-29T18:42:41.516272+00:00",
                            "mode": "MANUAL",
                            "operator": "Eva Green",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-28T18:43:01.789262+00:00",
                    "description": "Tank is filling",
                    "color": "#00BFFF",
                    "type": {
                        "id": 1,
                        "name": "Filling",
                        "description": "Tank is being filled",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW10",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "previousState": {
                            "id": 3,
                            "name": "Emptying",
                            "description": "Tank is being emptied",
                            "color": "#FFD700",
                            "type": {
                                "id": 3,
                                "name": "Emptying",
                                "description": "Tank is being emptied",
                            },
                        },
                        "additionalInfo": {
                            "runTime": 2669,
                            "lastFillTime": "2025-10-29T18:43:01.789282+00:00",
                            "mode": "MANUAL",
                            "operator": "Tom Lee",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-27T18:43:27.125067+00:00",
                    "description": "Tank is filling",
                    "color": "#00BFFF",
                    "type": {
                        "id": 1,
                        "name": "Filling",
                        "description": "Tank is being filled",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW10",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "previousState": {
                            "id": 5,
                            "name": "Maintenance",
                            "description": "Tank under maintenance",
                            "color": "#800080",
                            "type": {
                                "id": 5,
                                "name": "Maintenance",
                                "description": "Tank under maintenance",
                            },
                        },
                        "additionalInfo": {
                            "runTime": 664,
                            "lastFillTime": "2025-10-29T18:43:27.125086+00:00",
                            "mode": "AUTO",
                            "operator": "Alice Brown",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-26T18:43:42.345524+00:00",
                    "description": "Tank is low level",
                    "color": "#FF4500",
                    "type": {
                        "id": 4,
                        "name": "Low Level",
                        "description": "Tank water level is low",
                    },
                    "metadata": {
                        "source": "plc-controller",
                        "uri": "opc://plc1/DB1.DBW10",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "previousState": {
                            "id": 3,
                            "name": "Emptying",
                            "description": "Tank is being emptied",
                            "color": "#FFD700",
                            "type": {
                                "id": 3,
                                "name": "Emptying",
                                "description": "Tank is being emptied",
                            },
                        },
                        "additionalInfo": {
                            "runTime": 1948,
                            "lastFillTime": "2025-10-29T18:43:42.345542+00:00",
                            "mode": "MANUAL",
                            "operator": "Eva Green",
                        },
                    },
                },
            ],
        },
        {
            "elementId": "tank-201-alert",
            "displayName": "tank-201 Alert",
            "typeId": "alert-type",
            "namespaceUri": "https://abelara.com/equipment",
            "hasChildren": False,
            "relationships": {
                "HasParent": ["tank-201"],
            },
            "values": [
                {
                    "timestamp": "2025-10-29T18:44:17.833121+00:00",
                    "severity": 2,
                    "code": "LEVEL_LOW",
                    "message": "Tank water level below minimum threshold",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD44",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "acknowledgment": {
                            "acknowledged": False,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 19.2,
                            "warningThreshold": 3.5,
                            "alarmThreshold": 5.0,
                            "waterLevel": 3.84,
                            "minThreshold": 1.0,
                            "maxThreshold": 5.0,
                            "sensorLocation": "Tank Center",
                            "trend": "Falling",
                            "timeInAlarm": 4,
                            "recommendedAction": "Schedule maintenance",
                            "priority": "Critical",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-28T18:44:38.104100+00:00",
                    "severity": 3,
                    "code": "QUALITY_ALARM",
                    "message": "Water quality exceeds alarm threshold",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD44",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "acknowledgment": {
                            "acknowledged": True,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 20.1,
                            "warningThreshold": 3.5,
                            "alarmThreshold": 5.0,
                            "waterLevel": 3.74,
                            "minThreshold": 1.0,
                            "maxThreshold": 5.0,
                            "sensorLocation": "Tank Center",
                            "trend": "Rising",
                            "timeInAlarm": 8,
                            "recommendedAction": "Monitor",
                            "priority": "Low",
                        },
                    },
                },
                {
                    "timestamp": "2025-10-29T18:44:53.320437+00:00",
                    "severity": 3,
                    "code": "LEVEL_HIGH",
                    "message": "Tank water level exceeds maximum threshold",
                    "metadata": {
                        "source": "monitoring-system",
                        "uri": "opc://plc1/DB1.DBD44",
                        "asset": {
                            "id": 201,
                            "name": "Tank-201",
                            "description": "Raw water storage tank for process supply",
                        },
                        "acknowledgment": {
                            "acknowledged": False,
                            "acknowledgedBy": None,
                            "acknowledgedAt": None,
                        },
                        "additionalInfo": {
                            "temperature": 21.0,
                            "warningThreshold": 4.5,
                            "alarmThreshold": 5.0,
                            "waterLevel": 3.78,
                            "minThreshold": 1.0,
                            "maxThreshold": 5.0,
                            "sensorLocation": "Tank Center",
                            "trend": "Stable",
                            "timeInAlarm": 5,
                            "recommendedAction": "Check sensors",
                            "priority": "High",
                        },
                    },
                },
            ],
        },
        {
            "elementId": "sensor-001",
            "displayName": "TempSensor-101",
            "typeId": "sensor-type",
            "parentId": "cesmii-plant-1-utilities-water-system",
            "hasChildren": False,
            "namespaceUri": "https://thinkiq.com/equipment",
            "relationships": {"Monitors": ["tank-201"]},
            "values": [
                {
                    "value": 65.4,
                    "status": "GOOD",
                    "Timestamp": "2025-10-29T10:15:30Z",
                    "engUnit": "CEL",
                    "calibrationDate": "2025-01-15",
                },
                {
                    "value": 67.1,
                    "status": "GOOD",
                    "Timestamp": "2025-10-28T10:15:30Z",
                    "engUnit": "CEL",
                    "calibrationDate": "2025-01-15",
                },
                {
                    "value": 54.9,
                    "status": "GOOD",
                    "Timestamp": "2025-10-27T10:15:30Z",
                    "engUnit": "CEL",
                    "calibrationDate": "2025-01-15",
                },
                {
                    "value": 68.2,
                    "status": "GOOD",
                    "Timestamp": "2025-10-26T10:15:30Z",
                    "engUnit": "CEL",
                    "calibrationDate": "2025-01-15",
                },
            ],
        },
    ],
    "relationshipTypes": [
        {
            "elementId": "hierarchical-relationship-type",
            "displayName": "ParentChild",
            "namespaceUri": "https://cesmii.org/i3x",
            "directions": [
                {
                    "Subject": "HasChildren",
                    "Target": "HasParent",
                    "Cardinality": "1:0..1",
                },
                {
                    "Subject": "HasParent",
                    "Target": "HasChildren",
                    "Cardinality": "1..*:1",
                },
            ],
        },
        {
            "elementId": "inheritance-relationship-type",
            "displayName": "Inheritance",
            "namespaceUri": "https://cesmii.org/i3x",
            "directions": [
                {
                    "Subject": "InheritedBy",
                    "Target": "Inherits",
                    "Cardinality": "1:0..1",
                },
                {
                    "Subject": "InheritedFrom",
                    "Target": "InheritedBy",
                    "Cardinality": "1..*:1",
                },
            ],
        },
        {
            "elementId": "implementation-relationship-type",
            "displayName": "Implements",
            "namespaceUri": "https://cesmii.org/i3x",
            "directions": [
                {
                    "Subject": "ImplentedBy",
                    "Target": "Implements",
                    "Cardinality": "1:0..1",
                },
                {
                    "Subject": "ImplementedFrom",
                    "Target": "ImplementedBy",
                    "Cardinality": "1..*:1",
                },
            ],
        },
        {
            "elementId": "dependency-relationship-type",
            "displayName": "Dependency",
            "namespaceUri": "https://cesmii.org/i3x",
            "directions": [
                {
                    "Subject": "DependedOnBy",
                    "Target": "DependsOn",
                    "Cardinality": "1:0..1",
                },
                {
                    "Subject": "DependsOn",
                    "Target": "DependedOnBy",
                    "Cardinality": "1..*:1",
                },
            ],
        },
        {
            "elementId": "aggregation-relationship-type",
            "displayName": "Aggregates",
            "namespaceUri": "https://cesmii.org/i3x",
            "directions": [
                {
                    "Subject": "AggregatedBy",
                    "Target": "Aggregates",
                    "Cardinality": "1:0..1",
                },
                {
                    "Subject": "Aggregates",
                    "Target": "AggregatedBy",
                    "Cardinality": "1..*:1",
                },
            ],
        },
        {
            "elementId": "supply-relationship-type",
            "displayName": "Supply",
            "namespaceUri": "https://thinkiq.com/equipment",
            "directions": [
                {
                    "Subject": "SuppliesTo",
                    "Target": "SuppliedBy",
                    "Cardinality": "1..*:1..*",
                },
                {
                    "Subject": "SuppliedBy",
                    "Target": "SuppliesTo",
                    "Cardinality": "1..*:1..*",
                },
            ],
        },
        {
            "elementId": "monitoring-relationship-type",
            "displayName": "Monitoring",
            "namespaceUri": "https://thinkiq.com/equipment",
            "directions": [
                {
                    "Subject": "Monitors",
                    "Target": "MonitoredBy",
                    "Cardinality": "1..*:1..*",
                },
                {
                    "Subject": "MonitoredBy",
                    "Target": "Monitors",
                    "Cardinality": "1..*:1..*",
                },
            ],
        },
    ],
}