# I3X API Server

This is a Flask-based HTTP server that implements a REST API following the I3X (Industrial Information Interface eXchange) specification. The server provides endpoints for browsing equipment, sensors, and process data in a manufacturing environment. The server port is configurable via a config file.

## Project Structure

```
i3x/
├── app.py             # Main Flask application with I3X API implementation
├── config.json        # Configuration file for server settings
├── mock_data.py       # I3X-compliant mock data structures
├── requirements.txt   # Python dependencies
├── test_app.py        # Unit tests
├── setup.ps1          # PowerShell setup script
└── README.md          # This file
```

## Setting Up the Virtual Environment

### Prerequisites
- Python 3.7 or higher
- pip

### Setup Instructions

1. **Create a virtual environment**:

```powershell
# Navigate to the project directory
cd c:\Users\<user>\i3x

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate
```

2. **Install dependencies**:

```powershell
pip install -r requirements.txt
```

3. **Configure the server** (optional):

Edit `config.json` to change the port, host, or debug settings:

```json
{
    "port": 8080,
    "host": "0.0.0.0",
    "debug": true
}
```

4. **Run the server**:

```powershell
python app.py
```

The server will start on the configured port (default: 8080).

### Quick Setup with PowerShell Script

For convenience, you can use the included PowerShell script to set up and run the server with a single command:

```powershell
# Run the setup script
.\setup.ps1
```

This script will:
- Create a virtual environment (if it doesn't exist)
- Activate the virtual environment
- Install dependencies
- Start the server

## API Endpoints

The I3X server implements a subset of the Industrial Information Interface eXchange (I3X) specification. The available endpoints are described below.

### GET /browse

Returns I3X API data based on the requested resource type.

**Query Parameters**:
- `resource`: Type of resource to retrieve (`namespaces`, `objectTypes`, `instances`, `relationships`, or `all`)
- `namespaceUri`: (When `resource=objectTypes`) Filter object types by namespace URI
- `typeId`: (When `resource=instances`) Filter instances by type ID
- `type`: (When `resource=relationships`) Filter relationships by type (`hierarchical`, `nonHierarchical`, or `all`)

**Response Structure**:
- `status`: Operation result status ("success" or "error")
- `data`: The requested I3X data based on resource type
- `count`: Number of items returned (1 for non-array responses)
- `timestamp`: UTC timestamp of the response in ISO 8601 format

**Examples:**

```powershell
# Get all I3X data
curl http://localhost:8080/browse

# Get only namespaces
curl http://localhost:8080/browse?resource=namespaces

# Get instances of a specific type
curl http://localhost:8080/browse?resource=instances&typeId=machine-type-001

# Get object types from a specific namespace
curl http://localhost:8080/browse?resource=objectTypes&namespaceUri=http://i3x.org/mfg/equipment
```

Example response:
```json
{
    "status": "success",
    "data": {
        "namespaces": [...],
        "objectTypes": [...],
        "instances": [...],
        "relationships": {...}
    },
    "count": 1,
    "timestamp": "2025-07-07T10:15:30Z"
}
```

### GET /browse/instance/{elementId}

Returns data for a specific instance by its element ID.

**Example:**

```powershell
# Get a specific machine instance
curl http://localhost:8080/browse/instance/machine-001
```

Example response:
```json
{
    "status": "success",
    "data": {
        "elementId": "machine-001",
        "name": "CNC-101",
        "typeId": "machine-type-001",
        "parentId": "plant-001",
        "hasChildren": true,
        "namespaceUri": "http://i3x.org/mfg/equipment",
        "attributes": {
            "serialNumber": "SN-45678",
            "model": "ModelX",
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
    "timestamp": "2025-07-07T10:15:30Z"
}
```



## Running Tests

To run the unit tests, make sure your virtual environment is activated and dependencies are installed:

```powershell
# Activate the virtual environment if not already activated
.\venv\Scripts\Activate

# Run the tests
python -m unittest test_app.py
```

### Troubleshooting

If you encounter the error `ModuleNotFoundError: No module named 'flask'`, make sure you:

1. Have activated the virtual environment
2. Have installed the dependencies with `pip install -r requirements.txt`

## Advanced Usage

### Changing the Port

To run on a different port, modify the `config.json` file:

```json
{
    "port": 9000,
    "host": "0.0.0.0",
    "debug": true
}
```

### Mock Data

The server uses mock data stored in `mock_data.py` to simulate an I3X-compliant manufacturing data source. This includes:

- Namespaces (equipment, process, quality)
- Object Types (machines, sensors, processes)
- Object Instances (specific machines, sensors, and processes)
- Relationship definitions (hierarchical and non-hierarchical)

The mock data structure follows the Industrial Information Interface eXchange (I3X) specification as defined in the RFC, providing a realistic representation of manufacturing data.

### I3X Specification

This implementation follows the I3X specification which provides a common API that information platform vendors can implement to abstract vendor-specific implementations of data organization and contextualization into a set of standardized interfaces. The goal is to ensure applications written against one implementation can work against others, enabling portability and interoperability in manufacturing data systems.

The full specification document (`api.md`) is available as part of the Smart Manufacturing API Working Group RFC 001. The specification defines:

- Address space organization
- Object elements and their metadata
- Relationship types (hierarchical and non-hierarchical)
- Exploratory methods for browsing data
- Value methods for reading and writing data
- Subscription methods for real-time data

This implementation currently focuses on the exploratory methods, specifically the browse functionality for retrieving namespaces, object types, instances, and relationship definitions.


