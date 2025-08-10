# 📊 RediGuard Data Management Guide

This guide covers the integrated data management features that replace the standalone utility scripts.

## 🎯 Overview

RediGuard now includes comprehensive data management capabilities built directly into the FastAPI application. You can seed historical data, stream real-time events, and generate test batches all through API endpoints.

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
uv run uvicorn main:app --reload
```

### 2. Quick Test
```bash
# Run the quick test script
./scripts/test-data-management.sh

# Or run comprehensive tests
cd backend && python3 test_integrated_features.py
```

## 📋 Available Endpoints

### Data Generation

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/v1/data/generate-batch` | POST | Generate immediate batch of events | `count`, `anomaly_rate` |
| `/api/v1/data/seed` | POST | Seed historical data (background) | `num_events`, `anomaly_rate` |
| `/api/v1/data/stream/start` | POST | Start real-time streaming | `duration_minutes`, `events_per_minute`, `anomaly_rate` |
| `/api/v1/data/stream/stop` | POST | Stop active streaming | None |
| `/api/v1/data/stream/status` | GET | Check streaming status | None |

### Data Analysis

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/v1/data/stats` | GET | Get comprehensive statistics | None |
| `/api/v1/test/redis-features` | POST | Test all Redis 8 features | None |
| `/api/v1/alerts/search` | GET | Search security alerts | `limit`, `min_score`, etc. |

### Data Management

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/v1/data/clear` | DELETE | Clear all data (caution!) | `confirm=true` |

## 🔧 Usage Examples

### Immediate Event Generation
```bash
# Generate 10 events with 20% anomaly rate
curl -X POST "http://localhost:8000/api/v1/data/generate-batch?count=10&anomaly_rate=0.2"
```

### Historical Data Seeding
```bash
# Seed 1000 historical events over past 30 days
curl -X POST "http://localhost:8000/api/v1/data/seed?num_events=1000&anomaly_rate=0.1"
```

### Real-time Streaming
```bash
# Start streaming for 60 minutes at 20 events/minute
curl -X POST "http://localhost:8000/api/v1/data/stream/start?duration_minutes=60&events_per_minute=20&anomaly_rate=0.15"

# Check streaming status
curl -X GET "http://localhost:8000/api/v1/data/stream/status"

# Stop streaming
curl -X POST "http://localhost:8000/api/v1/data/stream/stop"
```

### Data Statistics
```bash
# Get comprehensive data statistics
curl -X GET "http://localhost:8000/api/v1/data/stats"
```

### Testing Redis Features
```bash
# Test all Redis 8 features
curl -X POST "http://localhost:8000/api/v1/test/redis-features"
```

## 📊 Data Models

### Event Generation Configuration

The system generates realistic login events with the following characteristics:

#### **User Profiles**
- 20 predefined users with unique behavior patterns
- Each user has typical locations, work hours, and IP ranges
- Behavior profiles include login frequency and risk tolerance

#### **Location Patterns**
- **Low Risk**: New York, San Francisco, London, Toronto, Berlin, Tokyo, Sydney
- **Medium Risk**: Mumbai, São Paulo
- **High Risk**: Moscow, Beijing, Lagos, Kiev
- **Very High Risk**: Tehran, Pyongyang

#### **IP Address Patterns**
- **Corporate**: `192.168.1.*`, `10.0.0.*`, `172.16.0.*`
- **Home**: `203.0.113.*`, `198.51.100.*`, `192.0.2.*`
- **VPN**: `185.220.*`, `91.207.*`, `104.244.*`
- **Suspicious**: `123.456.*`, `45.67.*`, `89.12.*`
- **Malicious**: `666.13.*`, `31.13.*`, `172.245.*`

#### **Anomaly Detection**
Events are classified as anomalous based on:
- Geographic impossibility (travel time violations)
- Unusual login times (outside work hours)
- High-risk locations
- Suspicious or malicious IP addresses
- Deviation from normal user behavior patterns

### Response Formats

#### Batch Generation Response
```json
{
  "message": "Generated 10 events",
  "events_processed": 10,
  "anomalies_detected": 3,
  "anomaly_rate_actual": 0.3,
  "events": [...]
}
```

#### Data Statistics Response
```json
{
  "redis_connected": true,
  "stream_length": 150,
  "total_alerts": 25,
  "malicious_ip_count": 5,
  "unique_users_timeseries": 12,
  "total_embeddings": 145,
  "streaming_active": false,
  "last_updated": "2025-08-10T09:30:00"
}
```

## 🔄 Background Tasks

### Historical Seeding
- Runs as FastAPI background task
- Generates events with timestamps distributed over past 30 days
- Processes events through full security pipeline
- Logs progress every 100 events

### Real-time Streaming
- Runs as FastAPI background task
- Configurable event rate and duration
- Automatic anomaly detection and logging
- Graceful stop capability

## 🛡️ Safety Features

### Rate Limiting
- Maximum 10,000 events for seeding
- Maximum 100 events per batch
- Maximum 100 events per minute for streaming
- Maximum 4 hours streaming duration

### Error Handling
- Comprehensive error responses
- Graceful degradation on failures
- Automatic cleanup of background tasks
- Redis connection health monitoring

### Data Protection
- Clear data endpoint requires explicit confirmation
- Background tasks are isolated and non-blocking
- Statistics endpoint is read-only and safe

## 🧪 Testing

### Unit Testing
The integrated features can be tested using:

```bash
# Comprehensive test suite
cd backend && python3 test_integrated_features.py

# Quick verification
./scripts/test-data-management.sh
```

### Manual Testing
```bash
# 1. Test health
curl http://localhost:8000/health

# 2. Generate test data
curl -X POST "http://localhost:8000/api/v1/data/generate-batch?count=5"

# 3. Check statistics
curl http://localhost:8000/api/v1/data/stats

# 4. Search alerts
curl "http://localhost:8000/api/v1/alerts/search?limit=5"
```

## 📈 Performance Considerations

### Memory Usage
- Background tasks use minimal memory
- Event generation is optimized for batch processing
- Redis operations are efficient and non-blocking

### Scalability
- Background tasks don't block API responses
- Configurable rates prevent system overload
- Graceful handling of Redis connection issues

### Monitoring
- Real-time statistics endpoint
- Comprehensive logging of all operations
- Health checks for all critical components

## 🔧 Troubleshooting

### Common Issues

**Background Task Not Starting**
- Check Redis connection: `curl http://localhost:8000/health`
- Verify parameters are within limits
- Check backend logs for errors

**No Events Generated**
- Ensure Redis is running and connected
- Check if security service is properly initialized
- Verify API endpoints are accessible

**Streaming Won't Stop**
- Use the stop endpoint: `curl -X POST http://localhost:8000/api/v1/data/stream/stop`
- Restart backend if necessary
- Check for background task errors in logs

### Debug Commands
```bash
# Check Redis connection
curl http://localhost:8000/health

# Test Redis features
curl -X POST http://localhost:8000/api/v1/test/redis-features

# Get current statistics
curl http://localhost:8000/api/v1/data/stats

# Check streaming status
curl http://localhost:8000/api/v1/data/stream/status
```

---

## 🎉 Migration from Utility Scripts

The following standalone scripts have been integrated into the API:

| Old Script | New Endpoint | Benefits |
|------------|--------------|----------|
| `seed_and_stream_data.py` | `/api/v1/data/*` | API-driven, background tasks, better control |
| `test_redis8_features.py` | `/api/v1/test/redis-features` | Integrated testing, JSON responses |

### Migration Benefits
- ✅ **API-First**: All functionality accessible via REST API
- ✅ **Background Processing**: Non-blocking operations
- ✅ **Better Control**: Start, stop, status endpoints
- ✅ **Integrated Monitoring**: Real-time statistics
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Documentation**: OpenAPI/Swagger integration
- ✅ **Testing**: Built-in test endpoints and scripts

This integration makes RediGuard more production-ready and easier to use in various deployment scenarios!
