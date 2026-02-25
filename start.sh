#!/bin/bash
# Railway start script
PORT=${PORT:-8000}
uvicorn source.main:app --host 0.0.0.0 --port $PORT
