#!/bin/bash

echo "🚀 Starting Rediguard with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to handle cleanup
cleanup() {
    echo "🛑 Stopping containers..."
    docker compose -f compose.dev.yml down
    exit 0
}

# Trap CTRL+C
trap cleanup INT

# Build and start services
echo "🔨 Building containers..."
docker compose -f compose.dev.yml build --no-cache

echo "🐳 Starting containers..."
docker compose -f compose.dev.yml up --remove-orphans

# If we get here, containers stopped normally
echo "✅ Containers stopped"
