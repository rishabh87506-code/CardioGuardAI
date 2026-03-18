#!/bin/bash

# CardioGuard AI - Unified App Startup Script

# Start Backend (Python Wellness Engine)
echo "🧠 Starting CardioGuard AI Brain (Python Backend)..."
cd "$(dirname "$0")/backend"
# Try to use the .venv if it exists, otherwise use system python
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
fi

# Run backend in background — exclude api-gateway/node_modules from reload watcher
python3 -m uvicorn app.main:app --reload --port 8000 \
  --reload-dir app \
  &
BACKEND_PID=$!

# Start API Gateway (Node.js BFF)
echo "🔗 Starting CardioGuard API Gateway (Node.js)..."
cd "$(dirname "$0")/backend/api-gateway"
node server.js &
GATEWAY_PID=$!

# Start Frontend
echo "💻 Starting CardioGuard AI Patient Portal (Frontend)..."
cd "$(dirname "$0")/frontend-patient"
npm run dev -- --port 5173 &
FRONTEND_PID=$!

echo "----------------------------------------------------"
echo "✅ CardioGuard AI is now running!"
echo "📍 Python Wellness Engine: http://localhost:8000"
echo "📍 API Gateway (BFF):     http://localhost:3000"
echo "📍 Patient Portal:        http://localhost:5173"
echo "----------------------------------------------------"
echo "Press Ctrl+C to stop all services."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $GATEWAY_PID $FRONTEND_PID; exit" INT
wait
