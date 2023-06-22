#!/bin/sh

# Start the server
uvicorn pypredict.main:app "--host" "0.0.0.0" "--port" "$SERVER_PORT" "--proxy-headers" "--forwarded-allow-ips" "*"
