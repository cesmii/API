# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- **Python version**: Requires Python 3.7+ but <3.13 (FastAPI/Pydantic compatibility issue with 3.13+)
- **Setup environment**: `./setup.sh` (Linux/Mac) or `.\setup.ps1` (Windows) - Creates venv, installs deps, starts server
- **Manual setup**: `python3 -m venv venv && ./venv/bin/activate && pip install -r requirements.txt`
- **Start server**: `python app.py` or `uvicorn app:app --host 0.0.0.0 --port 8080 --reload`
- **Run tests**: `python -m unittest test_app.py`
- **Docker build**: `docker build -t cesmii/api:dev .`
- **Docker run**: `docker run --rm -it -p 8080:8080 cesmii/api:dev`

### Configuration
- Server settings in `config.json` (port, host, debug mode)
- **App configuration**: `app` section contains configurable FastAPI metadata (title, description, version) - loaded at startup
- **Data source configuration**: Supports both single and multi-source configurations
  - **Single source**: `data_source.type` field determines which data source to use ("mock" or "mqtt")
  - **Multi-source**: `data_sources` object with named sources + `data_source_routing` for operation mapping
  - **Mock data source**: `{"type": "mock", "config": {}}` - Simulated data with random value updates
  - **MQTT data source**: `{"type": "mqtt", "config": {"mqtt_endpoint": "mqtt://host:port", "topics": ["#"]}}` - Real-time MQTT data
    - Supports `mqtt://` (plain) and `mqtts://` (TLS, accepts any certificate)
    - Topic wildcards: `#` (multi-level), `+` (single-level)
    - Converts topic `/` to `_` for API element IDs (e.g., `sensors/temp` → `sensors_temp`)
- Default port: 8080, accessible at http://localhost:8080/docs for Swagger UI

## Architecture Overview

This is a FastAPI-based I3X (Industrial Information Interface eXchange) API server implementing RFC 001 for Contextualized Manufacturing Information Platforms (CMIPs).

### Core Structure
- **app.py**: Main FastAPI application with startup/shutdown lifecycle and configurable data source initialization
- **models.py**: Pydantic models for all I3X RFC-compliant data structures
- **data_sources/**: Abstraction layer for data access
  - `data_interface.py`: Abstract I3XDataSource interface with methods for all RFC operations
  - `factory.py`: Factory pattern for creating single or multiple data sources from config
  - `manager.py`: DataSourceManager for routing operations across multiple data sources
  - `mock/`: Mock data source implementation with random value generation
    - `mock_data.py`: I3X-compliant simulated manufacturing data
    - `mock_data_source.py`: Mock implementation using mock_data.py
    - `mock_updater.py`: Background thread for generating random value updates
  - `mqtt/`: MQTT data source implementation with real-time updates
    - `mqtt_data_source.py`: Paho MQTT client, topic cache, and interface handlers (subscribes to one or more topics on a single broker)
- **routers/**: API endpoint implementations organized by functionality (use dependency injection for data access)
  - `namespaces.py`: Namespace operations (RFC 4.1.1)
  - `objectTypes.py`: Object type definitions and queries (RFC 4.1.2-4.1.3)
  - `objects.py`: Object instance queries (RFC 4.1.6-4.1.8)
  - `relationshipTypes.py`: Relationship type queries (RFC 4.1.4-4.1.5)
  - `subscriptions.py`: Real-time data streaming with QoS0/QoS2 support (RFC 4.2.3.x)

### Key Concepts
- **Namespaces**: Organize objects by domain (equipment, process, quality)
- **Object Types**: Define attributes and metadata for classes of objects
- **Object Instances**: Actual manufacturing objects with current attribute values
- **Subscriptions**: Background thread manages QoS0/QoS2 real-time data streaming
- **RFC Compliance**: All endpoints follow I3X RFC 001 specification exactly

### Data Flow
1. Data source(s) configured from `config.json` and created via `DataSourceFactory` at startup
   - Single source: Creates individual data source instance (mock or mqtt)
   - Multi-source: Creates `DataSourceManager` that routes operations to appropriate sources
2. Data source/manager injected into all router endpoints via FastAPI dependency injection using `get_data_source()` dependency
3. Operations automatically routed to configured data sources based on `data_source_routing` mapping
4. Subscription worker thread runs continuously for real-time updates using the configured data source
5. Data sources call `update_callback` when values change (MQTT messages, mock random updates)
6. Pydantic models ensure RFC-compliant JSON serialization

### Multi-Data Source Configuration

**Example Multi-Source Configuration:**
```json
{
  "data_sources": {
    "exploratory": {"type": "mock", "config": {}},
    "values": {"type": "database", "config": {"host": "db.example.com"}},
    "updates": {"type": "cache", "config": {"redis_url": "redis://localhost"}},
    "subscriptions": {"type": "streaming", "config": {"broker": "kafka://localhost"}}
  },
  "data_source_routing": {
    "primary": "exploratory",
    "get_namespaces": "exploratory",
    "get_object_types": "exploratory", 
    "get_instance_by_id": "values",
    "update_instance_values": "updates",
    "get_all_instances": "subscriptions"
  }
}
```

**Benefits:**
- **Operation-specific optimization**: Route read operations to read-optimized sources, writes to write-optimized sources
- **Scalability**: Distribute load across multiple backend systems
- **Flexibility**: Mix different data source types (databases, caches, message queues) for optimal performance
- **Backward compatibility**: Single-source configuration still supported

### Adding New Data Sources
1. Create a new subfolder in `data_sources/` (e.g., `data_sources/database/`)
2. Implement the `I3XDataSource` interface from `data_interface.py`
   - Required methods: `start()`, `stop()`, `get_namespaces()`, `get_object_types()`, `get_object_type_by_id()`, `get_instances()`, `get_instance_by_id()`, `get_related_instances()`, `get_hierarchical_relationships()`, `get_non_hierarchical_relationships()`, `update_instance_values()`, `get_all_instances()`
   - Call `update_callback` when values change to trigger subscription notifications
3. Update `DataSourceFactory._create_single_source()` in `factory.py` to import and handle the new type
4. Add the type name to `DataSourceFactory.get_supported_types()`
5. Add configuration examples to `config.json` for both single and multi-source setups
6. No router changes needed - dependency injection and routing handled transparently

Example structure for a new data source:
```
data_sources/
├── database/
│   ├── __init__.py
│   ├── database_source.py  # Implements I3XDataSource
│   └── connection.py
├── manager.py              # Routes operations to appropriate sources
├── mock/                   # Simulated data
└── mqtt/                   # Real MQTT broker
```

### Testing
- Uses unittest with FastAPI TestClient
- Tests cover all RFC 4.1.x exploratory methods and RFC 4.2.x value operations
- Includes streaming subscription test with threading