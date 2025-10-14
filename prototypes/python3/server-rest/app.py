import os
import json
import logging
import threading
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from routers.namespaces import ns
from routers.objectTypes import objTypes
from routers.relationshipTypes import relTypes
from routers.instances import instances
from routers.bulkOperations import bulk_ops
from routers.subscriptions import subs, subscription_worker, handle_data_source_update


from data_sources.factory import DataSourceFactory

# Load configuration helper function
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# Load config to get app settings
config = load_config()
app_config = config.get("app", {})

# Global flag for subscription thread
SUBSCRIPTION_THREAD_FLAG = {"running": True}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Initialize data source(s)
    try:
        # Try new multi-source configuration first
        if "data_sources" in config:
            data_source = DataSourceFactory.create_data_source(config)
            source_types = [f"{name}({cfg['type']})" for name, cfg in config['data_sources'].items()]
            print(f"Using MULTI-SOURCE configuration with {len(config['data_sources'])} sources: {', '.join(source_types)}")
        else:
            # Fall back to single source configuration
            data_source_config = config.get("data_source", {"type": "mock", "config": {}})
            data_source = DataSourceFactory.create_data_source(data_source_config)
            print(f"Using SINGLE-SOURCE configuration: {data_source_config['type'].upper()} data source")
    except Exception as e:
        print(f"Failed to initialize data source(s): {e}")
        print("Falling back to MOCK data source as fallback")
        data_source = DataSourceFactory.create_data_source({"type": "mock", "config": {}})
    
    # Set the data source in app state
    app.state.data_source = data_source
    
    # Create callback function that passes subscriptions to the handler
    def callback(update):
        handle_data_source_update(update, app.state.I3X_DATA_SUBSCRIPTIONS)
    
    # Start the data source with the callback
    data_source.start(callback)
    
    # Start subscription worker thread  
    threading.Thread(
        target=subscription_worker,
        args=(app.state.I3X_DATA_SUBSCRIPTIONS, SUBSCRIPTION_THREAD_FLAG),
        daemon=True
    ).start()
    yield
    # Shutdown
    SUBSCRIPTION_THREAD_FLAG["running"] = False
    
    # Stop the data source
    if hasattr(app.state, 'data_source'):
        app.state.data_source.stop()

app = FastAPI(
    title=app_config.get("title", "I3X API"),
    description=app_config.get("description", "Industrial Information Interface eXchange API - RFC 001 Compliant"),
    version=app_config.get("version", "1.0.0"),
    lifespan=lifespan
)

# Setup app state (data source will be set after config is loaded)
app.state.I3X_DATA_SUBSCRIPTIONS = []  # List[Subscription]

# Include namespaces
app.include_router(ns)
app.include_router(objTypes)
app.include_router(relTypes)
app.include_router(instances)
app.include_router(bulk_ops)
app.include_router(subs)


if __name__ == '__main__':
    import uvicorn
    
    config = load_config()
    port = config.get("port", 8080)
    debug = config.get("debug", False)
    host = config.get("host", "0.0.0.0")
    
    print(f"Starting server on {host}:{port} (debug: {debug})")
    print(f"Swagger page at http://localhost:{port}/docs")
    uvicorn.run("app:app", host=host, port=port, reload=debug)
