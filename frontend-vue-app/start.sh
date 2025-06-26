#!/bin/bash

echo "Starting frontend development server..."
cd "$(dirname "$0")" || exit
npm run dev
