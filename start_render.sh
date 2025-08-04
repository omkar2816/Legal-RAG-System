#!/bin/bash
# Script to start the server on Render.com

# Set default port if not provided by environment
PORT=${PORT:-8000}

# Always use 0.0.0.0 as host on Render
HOST="0.0.0.0"

echo "Starting server on $HOST:$PORT"

# Start the server without reload for production
exec python -m uvicorn api.main:app --host $HOST --port $PORT