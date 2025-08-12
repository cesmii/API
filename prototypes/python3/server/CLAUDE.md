# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- **Setup environment**: `./setup.sh` (Linux/Mac) or `.\setup.ps1` (Windows) - Creates venv, installs deps, starts server
- **Manual setup**: `python3 -m venv venv && ./venv/bin/activate && pip install -r requirements.txt`
- **Start server**: `python app.py` or `uvicorn app:app --host 0.0.0.0 --port 8080 --reload`
- **Run tests**: `python -m unittest test_app.py`

### Configuration
- Server settings in `config.json` (port, host, debug mode)
- **App configuration**: `app` section contains configurable FastAPI metadata (title, description, version) - loaded at startup
- **Data source configuration**: Supports both single and multi-source configurations
  - **Single source**: `data_source.type` field determines which data source to use
  - **Multi-source**: `data_sources` object with named sources + `data_source_routing` for operation mapping
- Default port: 8080, accessible at http://localhost:8080/docs for Swagger UI

## Architecture Overview

This is a FastAPI-based I3X (Industrial Information Interface eXchange) API server implementing RFC 001 for Contextualized Manufacturing Information Platforms (CMIPs).

### Core Structure
- **app.py**: Main FastAPI application with startup/shutdown lifecycle and configurable data source initialization
- **models.py**: Pydantic models for all I3X RFC-compliant data structures
- **data_sources/**: Abstraction layer for data access
  - `data_interface.py`: Abstract I3XDataSource interface
  - `factory.py`: Factory pattern for creating single or multiple data sources from config
  - `manager.py`: DataSourceManager for routing operations across multiple data sources
  - `mock/`: Mock data source implementation
    - `mock_data.py`: I3X-compliant simulated manufacturing data
    - `mock_data_source.py`: Mock implementation using mock_data.py
- **routers/**: API endpoint implementations organized by functionality (use dependency injection for data access)
  - `exploratory.py`: Browse equipment/sensors (RFC 4.1.x)
  - `values.py`: Read current/historical values (RFC 4.2.1.x)  
  - `updates.py`: Write operations (RFC 4.2.2.x)
  - `subscriptions.py`: Real-time data streaming (RFC 4.2.3.x)

### Key Concepts
- **Namespaces**: Organize objects by domain (equipment, process, quality)
- **Object Types**: Define attributes and metadata for classes of objects
- **Object Instances**: Actual manufacturing objects with current attribute values
- **Subscriptions**: Background thread manages QoS0/QoS2 real-time data streaming
- **RFC Compliance**: All endpoints follow I3X RFC 001 specification exactly

### Data Flow
1. Data source(s) configured from `config.json` and created via `DataSourceFactory` at startup
   - Single source: Creates individual data source instance
   - Multi-source: Creates `DataSourceManager` that routes operations to appropriate sources
2. Data source/manager injected into all router endpoints via FastAPI dependency injection
3. Operations automatically routed to configured data sources based on `data_source_routing` mapping
4. Subscription worker thread runs continuously for real-time updates using the configured data source
5. Pydantic models ensure RFC-compliant JSON serialization

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
2. Implement the `I3XDataSource` interface in your new subfolder
3. Update `DataSourceFactory._create_single_source()` to import and handle the new type
4. Add configuration examples to `config.json` for both single and multi-source setups
5. No router changes needed - dependency injection and routing handled transparently

Example structure for a new data source:
```
data_sources/
├── database/
│   ├── __init__.py
│   ├── database_source.py
│   └── connection.py
├── manager.py        # Routes operations to appropriate sources
└── mock/
    ├── __init__.py
    ├── mock_data.py
    └── mock_data_source.py
```

### Testing
- Uses unittest with FastAPI TestClient
- Tests cover all RFC 4.1.x exploratory methods and RFC 4.2.x value operations
- Includes streaming subscription test with threading