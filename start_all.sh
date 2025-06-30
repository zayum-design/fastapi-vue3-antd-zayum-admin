#!/bin/bash

# Start backend in background
echo "=== Starting Backend ==="
cd backend-fastapi-app
./start.sh &

# Start frontend in foreground (to see logs)
echo -e "\n=== Starting Frontend ==="
cd ../frontend-vue-app
./start.sh

echo -e "\n=== Development servers running ==="
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
