#!/bin/bash

echo "Starting backend with Supervisor..."
cd "$(dirname "$0")" || exit
supervisord -c supervisord.conf

echo "Backend is now running on http://localhost:8000"
