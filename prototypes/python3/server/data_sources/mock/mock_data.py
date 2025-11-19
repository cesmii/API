from datetime import datetime

# SIMPLIFIED I3X API compliant mock data - Industrial Information Interface eXchange (RFC 001)
I3X_DATA = {
    "namespaces": [
        {"uri": "https://cesmii.org/i3x", "displayName": "I3X"},
        {"uri": "https://isa.org/isa95", "displayName": "ISA95"},
        {"uri": "https://abelara.com/equipment", "displayName": "Abelara Equipment"},
        {"uri": "https://thinkiq.com/equipment", "displayName": "ThinkIQ Equipment"}
    ],
    "objectTypes": [
        {
            "elementId": "work-unit-type",
            "displayName": "WorkUnitType",
            "namespaceUri": "https://isa.org/isa95",
            "schema": "Namespaces/isa95.json#types/work-unit-type",
        },
        {
            "elementId": "state-type",
            "displayName": "StateType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/state-type",
        },
        {
            "elementId": "product-type",
            "displayName": "ProductType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/product-type",
        },
        {
            "elementId": "production-type",
            "displayName": "ProductionType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/production-type",
        },
        {
            "elementId": "measurements-type",
            "displayName": "MeasurementsType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/measurements-type"
        },
        {
            "elementId": "measurement-type",
            "displayName": "MeasurementType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/measurement-type"
        },
        {
            "elementId": "measurement-value-type",
            "displayName": "MeasurementValueType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/measurement-value-type"
        },
        {
            "elementId": "measurement-health-type",
            "displayName": "MeasurementHealthType",
            "namespaceUri": "https://abelara.com/equipment",
            "schema": "Namespaces/abelara.json#types/measurement-health-type"
        },
        {
            "elementId": "sensor-type",
            "displayName": "SensorType",
            "namespaceUri": "https://thinkiq.com/equipment",
            "schema": "Namespaces/thinkiq.json#types/sensor-type"
        },
    ],
    "instances": [
        {
            "elementId": "pump-101",
            "displayName": "pump-101",
            "namespaceUri": "https://isa.org/isa95",
            "typeId": "work-unit-type",
            #These two fields are required in the response so placed in the mock data for readability
            # A platform implementation would read its graph in order to populate these required response fields.
            "parentId": "/",
            "hasChildren": True,
            #This is where we maintain the graph relationships used above and in the /related endpoints
            "relationships": {
                "HasParent": "/",
                "HasChildren": [
                    "pump-101-state",
                    "pump-101-production",
                    "pump-101-measurements"
                ],
                "SuppliesTo": ["tank-201"],
            },
            # Optional property or attribute metadata (extra fields, per RFC 3.1.2 bullet 4)
            "operationStartDate": "July 1, 1980",
            "lastMaintainedDate": "August 1, 2001"
        },
        {
            "elementId": "pump-101-state",
            "displayName": "pump-101 State",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "state-type",
            "parentId": "pump-101",
            "hasChildren": False,
            "relationships": {
                "HasParent": "pump-101",
            },
            "records": [
                {
                    "value": {
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
                        },
                    },
                    #Values need metadata too, in fact some of the RFC 3.1.2 Object Metadata really belongs at the Value level
                    "quality": "GOOD",
                    #Our mock platform implementation was smart enough to lift this metadata from the payload. 
                    "timestamp": "2025-10-29T18:20:44.779036+00:00",
                },
                {
                    "value": {
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
                        },
                    },
                    "quality": "GOOD",
                    "timestamp": "2025-10-28T18:20:44.779036+00:00",
                },
                {
                    "value": {
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
                        },
                    },
                    "quality": "GOOD",
                    "timestamp": "2025-10-27T18:20:44.779036+00:00",
                },
            ],
        },
        {
            "elementId": "pump-101-production",
            "displayName": "pump-101 Production",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "production-type",
            "parentId": "pump-101",
            #In this case, we set hasChildren false to indicate that a value query should not recurse through the Composition relationship
            # This is an implementation choice on the part of a platform that limits or expands discoverability
            # TODO: Discuss with group!
            "hasChildren": False,
            "relationships": {
                "HasParent": "pump-101",
                #Class-composition relationship, shown at the instance level,
                # This indicates that pump-101-production data is a composition that includes another type of data
                "ComposedOf": [
                    "pump-101-production-product",
                ]
            },
        },
        {
            "elementId": "pump-101-production-product",
            "displayName": "pump-101 Product",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "product-type",
            #This parenthood is through the composition relationship, not a topological hierarchy
            # The RFC requires this member, but it should be understood in the context of the relationships defined below
            "parentId": "pump-101-production",
            "hasChildren": False,
            "relationships": {
                # The inclusion of ComposedBy and deliberate ommission of HasParent indicates a graph relationship and labels the edge
                "ComposedBy": ["pump-101-production"],
            },
        },
        {
            "elementId": "pump-101-measurements",
            "displayName": "pump-101 Measurements",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "measurements-type",
            "parentId": "pump-101",
            "hasChildren": True,
            "relationships": {
                "HasParent": "pump-101",
                "HasChildren": [
                    "pump-101-bearing-temperature",
                ],
            },
        },
        {
            "elementId": "pump-101-bearing-temperature",
            "displayName": "pump-101 Bearing Temperature",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "measurement-type",
            "parentId": "pump-101-measurements",
            "hasChildren": True,
            "relationships": {
                "HasParent": "pump-101-measurements",
                "HasChildren": ["pump-101-measurements-bearing-temperature-value", "pump-101-measurements-bearing-temperature-health"]
            },
            "records": [
                {
                    "value": {
                        "timestamp": "2025-10-29T18:32:47.673157+00:00",
                        "type": {
                            "id": 1,
                            "name": "Bearing Temperature",
                            "description": "Precision bearing temperature measurement",
                        },
                        "value": 70.34,
                        "health": 12,
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
                    "quality": "GOOD",
                    "timestamp": "2025-10-29T18:32:47.673157+00:00",
                },
                {
                    "value": {
                        "timestamp": "2025-10-28T18:32:47.673157+00:00",
                        "type": {
                            "id": 1,
                            "name": "Bearing Temperature",
                            "description": "Precision bearing temperature measurement",
                        },
                        "value": 71.79,
                        "health": 13,
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
                                "measurementDate": "2025-10-28T18:32:47.673173+00:00",
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
                    "quality": "GOOD",
                    "timestamp": "2025-10-28T18:32:47.673157+00:00",
                },
            ],
        },
        {
            "elementId": "pump-101-measurements-bearing-temperature-value",
            "displayName": "Pump 101 Bearing Temperature Value",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "measurement-value-type",
            "parentId": "pump-101-bearing-temperature",
            "hasChildren": False,
            "relationships": {
                "HasParent": "pump-101-bearing-temperature"
            },
            "records": [
                {
                    "value": 70.34,
                    "quality": "GOOD",
                    "timestamp": "2025-10-28T18:32:47.673157+00:00"
                },
                {
                    "value": 71.79,
                    "quality": "GOOD",
                    "timestamp": "2025-10-27T18:32:47.673157+00:00"
                }
            ],
             # Optional Object Metadata (RFC 3.1.2)
            "engUnit": "°F",
            "interpolation": "None"
        },
        {
            "elementId": "pump-101-measurements-bearing-temperature-health",
            "displayName": "Pump 101 Bearing Health",
            "namespaceUri": "https://abelara.com/equipment",
            "typeId": "measurement-health-type",
            "parentId": "pump-101-bearing-temperature",
            "hasChildren": False,
            "relationships": {
                "HasParent": "pump-101-bearing-temperature"
            },
            "records": [
                {
                    "value": 12,
                    "quality": "GOOD",
                    "timestamp": "2025-10-28T18:32:47.673157+00:00"
                },
                {
                    "value": 13,
                    "quality": "GOOD",
                    "timestamp": "2025-10-27T18:32:47.673157+00:00"
                }
            ]
        },
        {
            "elementId": "tank-201",
            "displayName": "tank-201",
            "namespaceUri": "https://isa.org/isa95",
            "typeId": "work-unit-type",
            "parentId": "/",
            "hasChildren": False,
            "relationships": {
                "SuppliedBy": "pump-101",
                "MonitoredBy": "sensor-001",
            },
        },
        {
            "elementId": "sensor-001",
            "displayName": "TempSensor-101",
            "namespaceUri": "https://thinkiq.com/equipment",
            "typeId": "sensor-type",
            "parentId": "/",
            "hasChildren": False,
            "relationships": {
                "Monitors": "tank-201"
            },
            "records": [
                {
                    "value": 67.1,
                    # Should these be specified (at least as optional)?
                    "quality": "GOOD",
                    "timestamp": "2025-10-28T10:15:30Z",
                    # Extra value-specific metadata may originate in the publisher's payload and is allowable
                    "localTimestamp": "2025-01-28T07:15:30-03:00",
                },
                {
                    "value": 54.9,
                    "quality": "GOOD",
                    "timestamp": "2025-10-27T10:15:30Z",
                    "localTimestamp": "2025-01-27T07:15:30-03:00",
                },
                {
                    "value": 68.2,
                    "quality": "GOOD",
                    "timestamp": "2025-10-26T10:15:30Z",
                    "localTimestamp": "2025-01-26T07:15:30-03:00",
                },
            ],
            # Optional Object Metadata (RFC 3.1.2)
            "engUnit": "CEL",
            "calibrationDate": "2025-01-15",
        },
    ],
    "relationshipTypes": [
        {
            "elementId": "HasParent",
            "displayName": "HasParent",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "HasChildren",
        },
        {
            "elementId": "HasChildren",
            "displayName": "HasChildren",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "HasParent"
        },
        {
            "elementId": "InheritedBy",
            "displayName": "InheritedBy",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "InheritsFrom"
        },
        {
            "elementId": "InheritsFrom",
            "displayName": "InheritsFrom",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "InheritedBy"
        },
        {
            "elementId": "ComposedOf",
            "displayName": "ComposedOf",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "ComposedBy"
        },
        {
            "elementId": "ComposedBy",
            "displayName": "ComposedBy",
            "namespaceUri": "https://cesmii.org/i3x",
            "reverseOf": "ComposedOf"
        },
        {
            "elementId": "Monitors",
            "displayName": "Monitors",
            "namespaceUri": "https://thinkiq.com/equipment",
            "reverseOf": "MonitoredBy"
        },
        {
            "elementId": "MonitoredBy",
            "displayName": "MonitoredBy",
            "namespaceUri": "https://thinkiq.com/equipment",
            "reverseOf": "Monitors"
        },
        {
            "elementId": "SuppliesTo",
            "displayName": "SuppliesTo",
            "namespaceUri": "https://thinkiq.com/equipment",
            "reverseOf": "SuppliedBy"
        },
        {
            "elementId": "SuppliedBy",
            "displayName": "SuppliedBy",
            "namespaceUri": "https://thinkiq.com/equipment",
            "reverseOf": "SuppliesTo"
        },
    ],
}
