#!/bin/sh

# Write environment variables to JS file
CONFIG="{
    \"WEBSOCKET_URL\": \"$WEBSOCKET_URL\",
}"
echo "window.config = $CONFIG" > /usr/src/app/pypredict/static/js/config.js

# Start the server
uvicorn pypredict.main:app "--host" "0.0.0.0" "--port" "8000"
