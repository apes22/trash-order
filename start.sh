#!/bin/bash
# Start both Node (Express) and Python (FastAPI) servers

SLING_PORT=${SLING_PORT:-8001}

# Run database migrations
echo "Running database migrations..."
npx prisma migrate deploy 2>&1

# Seed if needed
echo "Seeding database..."
node seed.js 2>&1

# Start FastAPI in background
echo "Starting Sling Scheduler (FastAPI) on port $SLING_PORT..."
python -m uvicorn sling.api:app --host 127.0.0.1 --port $SLING_PORT &
SLING_PID=$!

# Give FastAPI a moment to start
sleep 2

# Start Express in foreground
echo "Starting TIC Management (Express) on port $PORT..."
node server.js

# Clean up
kill $SLING_PID 2>/dev/null
