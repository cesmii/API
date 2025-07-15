# I3X API Server

This is a FastAPI-based HTTP server that implements the RFC 001 compliant I3X (Industrial Information Interface eXchange) API for Contextualized Manufacturing Information. The server provides endpoints for browsing equipment, sensors, and process data in a manufacturing environment. The server port is configurable via a config file.

## Project Structure

```
i3x/
├── app.py             # Main FastAPI application with I3X API implementation
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

Windows:
```powershell
# Navigate to the project directory
cd c:\Users\<user>\i3x

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate
```

Linux/Mac
```bash
# Navigate to the project directory
cd ~/i3x

# Create a virtual environemnt
python -m venv venv

# Activate the virtual environment
chmod +x ./venv/bin/activate
./venv/bin/activate
```

2. **Install dependencies**:

```
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

```
python app.py
```

Alternatively, you can run with uvicorn directly:

```
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

The server will start on the configured port (default: 8080).

### Quick Setup with PowerShell Script

For convenience, you can use the included scripts to set up and run the server with a single command:

Windows:
```powershell
# Run the setup script
.\setup.ps1
```

Linux/Mac:
```bash
# Run the setup script
chmox +x ./setup.sh
./setup.sh
```

This script will:
- Create a virtual environment (if it doesn't exist)
- Activate the virtual environment
- Install dependencies
- Start the server

## API Endpoints

The I3X server implements RFC 001 - Common API for Industrial Information Interface eXchange (I3X). The available endpoints follow the specification exactly. Check the interactive document to explore the API.

### Interactive Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

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

### RFC 001 Compliance

This implementation follows RFC 001 - Common API for Industrial Information Interface eXchange (I3X) which provides a common API that Contextualized Manufacturing Information Platforms (CMIPs) can implement. The specification defines:

- **Address Space Organization** (RFC 3) - Complete collection of contextualized information
- **Object Elements** (RFC 3.1) - Objects with attributes and required metadata
- **Object Relationships** (RFC 3.2) - Hierarchical and non-hierarchical relationships
- **Exploratory Methods** (RFC 4.1) - Read-only operations for browsing data
- **Value Methods** (RFC 4.2) - Reading current and historical values
- **Subscription Methods** (RFC 4.2.3) - Real-time data publishing (not yet implemented)

This implementation provides all required exploratory and value query methods as specified in the RFC, with proper metadata handling and JSON serialization as mandated by the specification.


