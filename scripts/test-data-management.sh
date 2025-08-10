#!/bin/bash

echo "🚀 RediGuard Data Management Quick Test"
echo "======================================"

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Please start it first:"
    echo "   cd backend && uv run uvicorn main:app --reload"
    exit 1
fi

echo ""
echo "📊 Current data statistics:"
curl -s http://localhost:8000/api/v1/data/stats | python3 -m json.tool

echo ""
echo "🧪 Testing Redis 8 features..."
curl -s -X POST http://localhost:8000/api/v1/test/redis-features | python3 -m json.tool

echo ""
echo "📦 Generating 5 test events..."
curl -s -X POST "http://localhost:8000/api/v1/data/generate-batch?count=5&anomaly_rate=0.4" | python3 -m json.tool

echo ""
echo "📊 Updated data statistics:"
curl -s http://localhost:8000/api/v1/data/stats | python3 -m json.tool

echo ""
echo "🔍 Searching for alerts..."
curl -s "http://localhost:8000/api/v1/alerts/search?limit=3" | python3 -m json.tool

echo ""
echo "✅ Quick test complete! 🎉"
echo ""
echo "💡 To run more comprehensive tests:"
echo "   cd backend && python3 test_integrated_features.py"
echo ""
echo "💡 To start data streaming:"
echo "   curl -X POST 'http://localhost:8000/api/v1/data/stream/start?duration_minutes=5&events_per_minute=20'"
echo ""
echo "💡 To seed historical data:"
echo "   curl -X POST 'http://localhost:8000/api/v1/data/seed?num_events=100&anomaly_rate=0.15'"
