#!/bin/bash

# Development startup script for Rediguard backend

echo "🚀 Starting Rediguard Backend Development Server"

# Check if Redis is running
echo "📡 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   docker compose up -d redis redisinsight"
    exit 1
fi

echo "✅ Redis is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
fi

# Activate virtual environment and run the server
echo "🐍 Starting FastAPI server with uv..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
