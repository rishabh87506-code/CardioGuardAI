#!/bin/bash

# CardioGuard AI - Unified App Startup Script

# Start Backend
echo "🚀 Starting CardioGuard AI Brain (Backend)..."
cd "$(dirname "$0")/backend"
# Try to use the .venv if it exists, otherwise use system python
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
fi

# Run backend in background
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "💻 Starting CardioGuard AI Patient Portal (Frontend)..."
cd "../frontend-patient"
npm run dev -- --port 5173 &
FRONTEND_PID=$!

echo "----------------------------------------------------"
echo "✅ CardioGuard AI is now running!"
echo "📍 Backend API: http://localhost:8000"
echo "📍 Patient Portal: http://localhost:5173"
echo "----------------------------------------------------"
echo "Press Ctrl+C to stop both services."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
