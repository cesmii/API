import os
import json
import threading
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from routers.exploratory import ns_exploratory
from routers.values import ns_values
from routers.updates import ns_updates
from routers.subscriptions import ns_subscriptions, subscription_worker

from mock_data import I3X_DATA

app = FastAPI(
    title="I3X API", 
    description="Industrial Information Interface eXchange API - RFC 001 Compliant",
    version="1.0.0"
)

# Setup app state
app.state.I3X_DATA = I3X_DATA
app.state.I3X_DATA_SUBSCRIPTIONS = []  # List[Subscription]
SUBSCRIPTION_THREAD_FLAG = {"running": True}

# Include namespaces
app.include_router(ns_exploratory)
app.include_router(ns_values)
app.include_router(ns_updates)
app.include_router(ns_subscriptions)

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

config = load_config()

# Start & stop to manage the subscription thread
@app.on_event("startup")
def start_subscription_thread():
    threading.Thread(
        target=subscription_worker,
        args=(app.state.I3X_DATA_SUBSCRIPTIONS, app.state.I3X_DATA, SUBSCRIPTION_THREAD_FLAG),
        daemon=True
    ).start()

@app.on_event("shutdown")
def stop_subscription_thread():
    SUBSCRIPTION_THREAD_FLAG["running"] = False

if __name__ == '__main__':
    import uvicorn
    
    port = config.get("port", 8080)
    debug = config.get("debug", False)
    host = config.get("host", "0.0.0.0")
    
    print(f"Starting server on {host}:{port} (debug: {debug})")
    uvicorn.run("app:app", host=host, port=port, reload=debug)
