from flask import Flask, jsonify, request
import os
import json
from datetime import datetime, timezone
from mock_data import I3X_DATA

app = Flask(__name__)

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

config = load_config()

@app.route('/browse', methods=['GET'])
def browse():
    """REST endpoint that returns I3X API data"""
    resource = request.args.get('resource', 'all')
    
    if resource == 'namespaces':
        result_data = I3X_DATA['namespaces']
    elif resource == 'objectTypes':
        namespace_uri = request.args.get('namespaceUri')
        if namespace_uri:
            result_data = [t for t in I3X_DATA['objectTypes'] if t['namespaceUri'] == namespace_uri]
        else:
            result_data = I3X_DATA['objectTypes']
    elif resource == 'instances':
        type_id = request.args.get('typeId')
        if type_id:
            result_data = [i for i in I3X_DATA['instances'] if i['typeId'] == type_id]
        else:
            result_data = I3X_DATA['instances']
    elif resource == 'relationships':
        relation_type = request.args.get('type', 'all')
        if relation_type == 'hierarchical':
            result_data = {"relationshipTypes": I3X_DATA['relationships']['hierarchical']}
        elif relation_type == 'nonHierarchical':
            result_data = {"relationshipTypes": I3X_DATA['relationships']['nonHierarchical']}
        else:
            result_data = I3X_DATA['relationships']
    else:
        # Return all I3X data
        result_data = I3X_DATA
    
    return jsonify({
        "status": "success",
        "data": result_data,
        "count": len(result_data) if isinstance(result_data, list) else 1,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    })

@app.route('/browse/instance/<string:element_id>', methods=['GET'])
def get_instance(element_id):
    """Get a specific instance by its elementId"""
    for instance in I3X_DATA['instances']:
        if instance['elementId'] == element_id:
            return jsonify({
                "status": "success",
                "data": instance,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })
    
    return jsonify({
        "status": "error",
        "message": f"Instance with elementId '{element_id}' not found",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }), 404





if __name__ == '__main__':
    port = config.get("port", 8080)
    debug = config.get("debug", False)
    host = config.get("host", "0.0.0.0")
    
    print(f"Starting server on {host}:{port} (debug: {debug})")
    app.run(host=host, port=port, debug=debug)
