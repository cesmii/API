# I3X API - Industrial Information Interface eXchange

## Project Overview

This is a FastAPI-based implementation of the I3X API (RFC 001), providing a standardized interface for industrial information exchange. The API supports multiple data sources (mock, MQTT) with a pluggable architecture and implements both exploratory and subscription-based data access patterns.

## Architecture

### Core Components

1. **FastAPI Application** (`app.py`)
   - Lifespan context manager handles startup/shutdown
   - Dependency injection for data sources
   - Multiple routers for different endpoint groups

2. **Data Source Architecture**
   - Abstract interface: `data_sources/data_interface.py`
   - Factory pattern: `data_sources/factory.py`
   - Implementations:
     - Mock: `data_sources/mock/mock_data_source.py`
     - MQTT: `data_sources/mqtt/mqtt_data_source.py`
   - Multi-source support via `data_sources/manager.py`

3. **Routers**
   - `routers/namespaces.py` - Namespace discovery
   - `routers/typeDefinitions.py` - Type schemas
   - `routers/objects.py` - Object instance queries (explore, query, update)
   - `routers/subscriptions.py` - QoS0 (SSE) and QoS2 (polling) subscriptions

## Key Concepts

### Composition vs Organization Relationships

**Composition (ComposedOf/ComposedBy)**:
- Used when child data IS part of the parent's definition
- Parent has `isComplex: True`
- Children contribute to the parent's value
- Example: `pump-101` is composed of state, production, and measurements
- Example: `measurement-type` is composed of value and health subtypes

**Organization (HasChildren/HasParent)**:
- Used for hierarchical organization
- Parent typically has `isComplex: False`
- Children are separate entities
- Example: `pump-station` has children `pump-101`, `tank-201`

### maxDepth Parameter

Controls recursion depth when fetching values through ComposedOf relationships:
- `maxDepth=0` - Infinite recursion (include all nested composed elements)
- `maxDepth=1` - No recursion (just this element's value) - this is the default
- `maxDepth=N` (N>1) - Recurse up to N levels deep

**Implementation**:
- `routers/objects.py` - value query endpoints (`/value`, `/history`)
- `routers/subscriptions.py` - subscription system
- `routers/utils.py` - `getSubscriptionValue()` helper
- `data_sources/mock/mock_data_source.py` - recursive value fetching

**Key Behavior**:
- Always includes composed children even if they have no value (uses `{}` placeholder)
- Own value is stored under `_value` key when recursing
- Child values are keyed by their elementId

## Mock Data Source

### Structure

**Location**: `data_sources/mock/mock_data.py`

Contains:
- `namespaces` - Namespace definitions
- `objectTypes` - Type definitions
- `instances` - Object instances
- `relationshipTypes` - Relationship type definitions

### Mock Data Updater

**Critical Implementation Detail** (Bug fixed Dec 2024):

The `MockDataUpdater` generates random value changes every second to simulate real-time data.

**Bug**: Originally called `get_all_instances()` which filters out the `records` field, causing the updater to find 0 instances with records.

**Fix** (`data_sources/mock/mock_updater.py:37`):
```python
# CORRECT - Access raw data with records
instances = self.data_source.data["instances"]

# WRONG - This filters out records!
# instances = self.data_source.get_all_instances()
```

**Why**: `get_all_instances()` deliberately removes records to keep exploratory API responses clean, but the updater needs records to modify them.

### Type Patterns in Mock Data

Based on schema/data review (Dec 2024):

1. **Simple Value Types** (has records, not complex)
   - `sensor-type` - simple numeric values
   - `measurement-value-type` - numeric measurement values
   - `measurement-health-type` - integer health indicators

2. **Complex Value Types** (has records AND composed children)
   - `measurement-type` - has tolerance/inTolerance records + composed of value/health children
   - `state-type` - complex state objects with metadata

3. **Composite Containers** (no records, only composed children)
   - `measurements-type` - container composed of measurement-type children
   - `work-unit-type` - can be simple or complex with ComposedOf relationships

4. **Organizational Containers** (no records, HasChildren relationships)
   - `production-type` - organizational container with HasChildren
   - `product-type` - metadata container
   - `work-center-type` - organizational container

## Schema System

**Location**: `data_sources/mock/Namespaces/*.json`

### Schema Files

1. **abelara.json** - Equipment/manufacturing types
   - state-type, product-type, production-type
   - measurements-type, measurement-type, measurement-value-type, measurement-health-type

2. **isa95.json** - ISA-95 types
   - work-center-type, work-unit-type

3. **thinkiq.json** - Sensor types
   - sensor-type

### Relationship Annotations

Use `!related` field to document composition/organizational relationships:

```json
{
  "type-name": {
    "type": "object",
    "!related": {
      "relationshipType": "ComposedOf",
      "types": [
        "https://namespace:child-type"
      ]
    }
  }
}
```

**Note**: The `!` prefix indicates metadata/relationship information, not actual data properties.

## Subscription System

### QoS Levels

**QoS0** (Server-Sent Events):
- Real-time streaming via SSE
- Updates pushed immediately when data changes
- Endpoint: `POST /subscriptions/{id}/objects` returns `StreamingResponse`
- Requires `MockDataUpdater` to be running for updates

**QoS2** (Polling):
- Client polls for updates via sync endpoint
- Updates queued in `pendingUpdates` array
- Endpoints:
  - `POST /subscriptions/{id}/objects` - register items
  - `POST /subscriptions/{id}/sync` - poll for updates

### Update Flow

1. Data source calls callback when values change
2. `handle_data_source_update()` routes to active subscriptions
3. For QoS0: Immediately pushes to SSE stream via handler
4. For QoS2: Queues in `pendingUpdates` for next sync

## Testing

### Test Structure

**File**: `test_app.py`

**Setup**: Uses `TestClient` with class-level setup to properly trigger lifespan events:

```python
@classmethod
def setUpClass(cls):
    cls.client = TestClient(app)
    cls.client.__enter__()  # Triggers lifespan startup

@classmethod
def tearDownClass(cls):
    cls.client.__exit__(None, None, None)  # Triggers lifespan shutdown
```

**Why**: FastAPI lifespan events (which start data sources and updaters) only run when TestClient is used as a context manager.

### Test Coverage

- Namespace endpoints
- Type definition endpoints
- Object instance queries (with correct IDs from mock data)
- Value queries with `maxDepth`
- Relationship queries
- QoS0 subscription streaming (requires MockDataUpdater)
- QoS2 subscription polling

### Running Tests

```bash
source venv/bin/activate
python -m pytest test_app.py -v
```

**Expected**: 8/8 tests passing (as of Dec 2024)

## Recent Changes (December 2024)

### 1. maxDepth Implementation
- Replaced `includeMetadata` boolean with `maxDepth` integer
- Enables recursive traversal of ComposedOf relationships
- `maxDepth=0` for infinite recursion, `maxDepth=1` (default) for no recursion
- Returns nested structure with `_value` for own data and child keys for composed data

### 2. MockDataUpdater Bug Fix
- Fixed updater to access raw data instead of filtered instances
- Now properly generates updates every second
- QoS0 subscriptions now receive real-time updates

### 3. Schema Consistency Review
- Fixed product-type, production-type, measurements-type schemas to match mock data
- Added `!related` relationship annotations to all composite types
- Clarified distinction between container types and value types

### 4. Test Suite Updates
- Fixed all endpoint paths to match current API
- Updated TestClient initialization to trigger lifespan
- Corrected test data to use actual mock instance IDs
- All 8 tests now passing

## Configuration

**File**: `config.json`

Supports two modes:

1. **Single Data Source**:
```json
{
  "data_source": {
    "type": "mock",
    "config": {}
  }
}
```

2. **Multi-Source** (different sources for different capabilities):
```json
{
  "data_sources": {
    "exploratory": {"type": "mock"},
    "values": {"type": "mqtt", "config": {...}},
    "updates": {"type": "mqtt"},
    "subscriptions": {"type": "mock"}
  }
}
```

## Key Files Reference

- `app.py` - Main application with lifespan management
- `models.py` - Pydantic models for requests/responses
- `routers/` - API endpoint implementations
- `data_sources/` - Data source implementations and interfaces
- `data_sources/mock/mock_data.py` - Mock data definitions
- `data_sources/mock/mock_updater.py` - Value change generator
- `data_sources/mock/Namespaces/` - JSON schemas
- `test_app.py` - API test suite

## Development Notes

### Adding New Mock Data

1. Add instance to `mock_data.py` `instances` array
2. Define `typeId` (must exist in a Namespace schema)
3. Set `isComplex` based on ComposedOf relationships
4. Add `records` array if type has values (VQT format)
5. Define `relationships` (ComposedOf, HasChildren, etc.)

### Adding New Types

1. Create/update JSON schema in `Namespaces/`
2. Define `type` (usually "object" or primitive)
3. Add `!related` annotation if composite/organizational
4. Add `properties` only for actual data fields (not children)
5. Ensure schema matches how instances use records

### Debugging Subscription Issues

If QoS0 subscriptions don't receive updates:
1. Verify `MockDataUpdater` is running (check app startup logs)
2. Ensure instance has `records` in mock_data.py
3. Check instance is not marked `"static": true`
4. Verify subscription's `monitoredItems` includes the elementId
5. Confirm `handle_data_source_update` is being called

## Important Patterns

### Value Query with Recursion
```python
# GET /objects/{elementId}/value?maxDepth=0  (infinite recursion)
# GET /objects/{elementId}/value?maxDepth=3  (recurse 3 levels)
{
  "_value": {...},  # Own value
  "child-1": {...}, # First child's value
  "child-2": {      # Second child's value (potentially recursive)
    "_value": {...},
    "grandchild-1": {...}
  }
}
```

### VQT (Value-Quality-Timestamp) Format
```python
{
  "value": <any>,          # The actual value (primitive or object)
  "quality": "GOOD",       # Quality indicator
  "timestamp": "2025-..." # ISO 8601 timestamp
}
```

### Subscription Registration
```python
# 1. Create subscription
POST /subscriptions {"qos": "QoS0"}
→ {"subscriptionId": 0}

# 2. Register monitored items
POST /subscriptions/0/objects {
  "elementIds": ["sensor-001"],
  "maxDepth": 1  # 0=infinite, 1=no recursion (default), N=recurse N levels
}
→ StreamingResponse (QoS0) or confirmation (QoS2)

# 3. For QoS2, poll for updates
POST /subscriptions/0/sync
→ [{elementId, value, quality, timestamp}, ...]
```

## API Conventions

- Element IDs are strings (e.g., "pump-101")
- Namespace URIs use https:// scheme
- Type IDs reference types within namespaces
- Relationships use standard types: ComposedOf, ComposedBy, HasChildren, HasParent, Monitors, MonitoredBy, etc.
- maxDepth=0 means infinite recursion (all composed children)
- maxDepth=1 means no recursion (just the element's own value) - this is the default
- Empty composed children return `{}` not `null`
