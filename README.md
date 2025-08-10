# 🛡️ RediGuard - Real-Time Security & Threat Detection

[![CI/CD Pipeline](https://github.com/ajitpdevops/rediguard/actions/workflows/test.yml/badge.svg)](https://github.com/ajitpdevops/rediguard/actions)
[![Deploy to AWS](https://github.com/ajitpdevops/rediguard/actions/workflows/deploy.yml/badge.svg)](https://github.com/ajitpdevops/rediguard/actions)

A cutting-edge real-time security monitoring and threat detection system powered by **Redis 8** and **AI/ML**. RediGuard combines advanced Redis data structures with machine learning to detect suspicious login patterns, anomalous behaviors, and potential security threats in real-time.

## 🎯 Overview

RediGuard demonstrates how Redis 8's powerful features can be leveraged for cybersecurity applications:

- **Real-time event processing** using Redis Streams
- **AI-powered anomaly detection** with vector similarity search
- **Time-series analysis** for pattern recognition
- **Bloom filters** for efficient blacklist checking
- **JSON storage** for complex alert data
- **Full-text search** for alert querying and analysis

## ✨ Features

### 🔒 Security Monitoring
- Real-time login event ingestion and processing
- Geolocation-based anomaly detection (impossible travel scenarios)
- IP address reputation checking via Bloom filters
- User behavior pattern analysis using AI embeddings

### 📊 Analytics & Insights
- Interactive dashboard with real-time updates
- Historical trend analysis with time-series data
- Advanced search and filtering of security alerts
- Visual representation of threat landscapes

### 🚀 Performance & Scalability
- Redis 8 powered for sub-millisecond response times
- Containerized architecture for easy deployment
- Horizontal scaling capabilities
- CI/CD pipeline for automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Redis 8     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (All Modules) │
│                 │    │                 │    │                 │
│ - Dashboard     │    │ - API Routes    │    │ - Streams       │
│ - Real-time UI  │    │ - AI Processing │    │ - TimeSeries    │
│ - Charts        │    │ - Event Workers │    │ - Vector Search │
└─────────────────┘    └─────────────────┘    │ - Bloom Filters │
                                              │ - JSON Documents│
                                              │ - Search Index  │
                                              └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Redis 8** - In-memory data store with advanced modules
- **scikit-learn** - Machine learning for anomaly detection
- **NumPy** - Numerical computing for vector operations
- **Pydantic** - Data validation and settings management

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Composable charting library
- **Radix UI** - Low-level UI primitives

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline
- **AWS ECR** - Container registry
- **Redis Insights** - Redis monitoring and debugging

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Node.js 22+** (for local development)
- **Python 3.12+** (for local development)
- **Git** for version control

### 1. Clone the Repository

```bash
git clone https://github.com/ajitpdevops/rediguard.git
cd rediguard
```

### 2. Start with Docker Compose (Recommended)

```bash
# Start all services in development mode
./start-dev.sh

# Or manually with Docker Compose
docker compose -f compose.dev.yml up --build
```

### 3. Access the Application

- 🌐 **Frontend Dashboard**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📊 **API Documentation**: http://localhost:8000/docs
- 🔍 **Redis Insights**: http://localhost:5540

### 4. Initialize Demo Data

```bash
# Generate sample security events (small batch)
curl -X POST "http://localhost:8000/api/v1/data/generate-batch?count=10&anomaly_rate=0.2"

# Seed historical data (background task)
curl -X POST "http://localhost:8000/api/v1/data/seed?num_events=1000&anomaly_rate=0.1"

# Start real-time streaming (background task)
curl -X POST "http://localhost:8000/api/v1/data/stream/start?duration_minutes=60&events_per_minute=20&anomaly_rate=0.15"

# Check data statistics
curl -X GET "http://localhost:8000/api/v1/data/stats"
```

## 📊 Data Management Features

RediGuard now includes comprehensive data management capabilities built directly into the API:

### **Historical Data Seeding**
- Generates realistic historical login events over the past 30 days
- Configurable number of events and anomaly rates
- Runs as background tasks to avoid blocking the API
- Creates user behavior profiles for realistic patterns

### **Real-time Data Streaming** 
- Simulates live login events at configurable rates
- Background streaming with start/stop controls
- Configurable duration and event frequency
- Real-time anomaly detection and alerting

### **Batch Event Generation**
- Generate immediate batches of events for testing
- Instant processing and results
- Perfect for demonstrations and quick testing

### **Comprehensive Statistics**
- Real-time data insights and metrics
- Redis health and performance monitoring
- Stream lengths, alert counts, and more

### **Data Management Examples**

```bash
# Quick test with 5 events
curl -X POST "http://localhost:8000/api/v1/data/generate-batch?count=5&anomaly_rate=0.4"

# Seed 500 historical events with 15% anomaly rate
curl -X POST "http://localhost:8000/api/v1/data/seed?num_events=500&anomaly_rate=0.15"

# Stream for 30 minutes at 30 events/minute
curl -X POST "http://localhost:8000/api/v1/data/stream/start?duration_minutes=30&events_per_minute=30&anomaly_rate=0.2"

# Check streaming status
curl -X GET "http://localhost:8000/api/v1/data/stream/status"

# Stop streaming
curl -X POST "http://localhost:8000/api/v1/data/stream/stop"

# Get comprehensive statistics
curl -X GET "http://localhost:8000/api/v1/data/stats"

# Test all Redis 8 features
curl -X POST "http://localhost:8000/api/v1/test/redis-features"
```

## 🔧 Development Setup

### Backend Development

```bash
cd backend

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -r requirements.txt

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

### Redis Setup

```bash
# Start Redis 8 with all modules
docker run -d --name redis-stack \
  -p 6379:6379 -p 5540:5540 \
  redis:8.2-rc1-alpine

# Or use Redis Stack for full feature set
docker run -d --name redis-stack \
  -p 6379:6379 -p 8001:8001 \
  redis/redis-stack:8.2-RC1
```

## 📖 API Documentation

### Core Endpoints

- `GET /health` - Health check endpoint
- `GET /api/v1/events` - Retrieve security events
- `GET /api/v1/alerts` - Get security alerts
- `GET /api/v1/users` - User analytics
- `POST /api/v1/events/login` - Process login events
- `GET /api/v1/alerts/search` - Search security alerts
- `GET /api/v1/users/{user_id}/anomaly-history` - Get user anomaly history
- `GET /api/v1/users/{user_id}/similar-behavior` - Find similar behavior patterns

### Data Management Endpoints

- `POST /api/v1/data/seed` - Seed historical data for testing
- `POST /api/v1/data/stream/start` - Start real-time data streaming
- `POST /api/v1/data/stream/stop` - Stop active data streaming
- `GET /api/v1/data/stream/status` - Get streaming status
- `POST /api/v1/data/generate-batch` - Generate batch of events immediately
- `GET /api/v1/data/stats` - Get comprehensive data statistics
- `POST /api/v1/test/redis-features` - Test all Redis 8 features
- `DELETE /api/v1/data/clear` - Clear all data (use with caution)

### Security Endpoints

- `POST /api/v1/security/add-malicious-ip` - Add IP to blocklist
- `GET /api/v1/security/check-ip/{ip}` - Check IP reputation
- `GET /api/v1/ip/{ip}/reputation` - Get IP reputation details

### WebSocket Endpoints

- `ws://localhost:8000/ws` - Real-time event stream

### Authentication

Currently using development mode. In production, implement:
- JWT tokens for API authentication
- OAuth2 for user management
- Role-based access control (RBAC)

## 🏢 Redis 8 Features Utilized

RediGuard successfully integrates **Redis Stack 8** with advanced data structures for real-time security monitoring:

### ✅ **Implementation Status**

| Feature | Status | Purpose | Implementation |
|---------|--------|---------|---------------|
| **Streams** | ✅ Active | Real-time event ingestion | `XADD logins:stream * user_id u001 ip 1.2.3.4` |
| **TimeSeries** | ✅ Active | Historical anomaly tracking | `TS.ADD timeseries:u001:anomaly 1691553792 0.92` |
| **Vector Search** | ✅ Active | Behavior pattern similarity | `FT.SEARCH embeddings "@vector:[...] KNN 5"` |
| **JSON** | ✅ Active | Complex alert storage | `JSON.SET alert:u001:ts $ '{...}'` |
| **Search** | ✅ Active | Alert querying & filtering | `FT.SEARCH alerts "@score:[0.8 +inf]"` |
| **Bloom Filter** | ⚠️ Fallback | Fast IP blacklist checking | `BF.EXISTS bad_ips:bloom 1.2.3.4` (using Redis Sets) |

### 🚀 **Key Redis 8 Features in Action**

#### **Real-time Event Processing with Streams**
```python
# Add login event to stream
stream_id = redis.xadd("logins:stream", {
    "user_id": "alice",
    "ip": "192.168.1.100", 
    "location": "New York",
    "timestamp": "1691553792"
})

# Process with consumer groups
events = redis.xreadgroup("security", "analyzer", {"logins:stream": ">"})
```

#### **Time-Series Anomaly Tracking**
```python
# Create TimeSeries for user
redis.execute_command("TS.CREATE", "timeseries:alice:anomaly", 
                     "RETENTION", 86400000,
                     "LABELS", "user", "alice", "metric", "anomaly_score")

# Add anomaly score
redis.execute_command("TS.ADD", "timeseries:alice:anomaly", timestamp, 0.85)

# Query time range
scores = redis.execute_command("TS.RANGE", "timeseries:alice:anomaly", start_time, end_time)
```

#### **Rich Document Storage with JSON**
```python
# Store alert as JSON document
alert_data = {
    "user_id": "alice",
    "ip": "192.168.1.100",
    "score": 0.85,
    "location": "New York",
    "timestamp": 1691553792,
    "is_malicious_ip": False
}
redis.execute_command("JSON.SET", "alert:123", "$", json.dumps(alert_data))
```

#### **Advanced Search with Vector Similarity**
```python
# Create search index with vector field
redis.execute_command("FT.CREATE", "embeddings_idx",
                     "ON", "HASH",
                     "SCHEMA", 
                     "embedding", "VECTOR", "HNSW", "6",
                     "TYPE", "FLOAT32", "DIM", "16", "DISTANCE_METRIC", "COSINE")

# Vector similarity search
result = redis.execute_command("FT.SEARCH", "embeddings_idx",
                              "*=>[KNN 5 @embedding $query_vector AS distance]")
```

### 🏗️ **Redis Stack Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Rediguard Backend                        │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Application                                       │
│  ├── Redis Stack Client (redis_stack.py)                  │
│  ├── Security Service (security_service.py)               │
│  ├── AI Service (ai_service.py)                           │
│  └── API Routes (routes.py)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Redis Stack 8                            │
├─────────────────────────────────────────────────────────────┤
│  🕰️  TimeSeries  │ User anomaly scores over time         │
│  📄 JSON         │ Rich security alert documents         │
│  🔍 Search       │ Full-text + Vector search indexes     │
│  📊 Streams      │ Real-time login event processing      │
│  🌸 Bloom        │ Malicious IP detection (fallback)     │
└─────────────────────────────────────────────────────────────┘
```

### 📊 **Module Availability Check**

You can verify which Redis 8 modules are available by calling:
```bash
# Check Redis modules status
curl http://localhost:8000/api/v1/test/redis-features
```

Expected response:
```json
{
  "redis_connected": true,
  "modules_available": {
    "search": true,      // ✅ RediSearch with vector support
    "timeseries": true,  // ✅ Redis TimeSeries  
    "json": true,        // ✅ RedisJSON
    "bloom": false,      // ⚠️ Using fallback (Redis Sets)
    "graph": false       // ➖ Not needed for this MVP
  }
}
```

## 📊 Data Models

### Login Events (Redis Streams)
```json
{
  "user_id": "u001",
  "ip": "91.23.44.56",
  "location": "New York, US",
  "timestamp": 1691553792,
  "user_agent": "Mozilla/5.0...",
  "session_id": "sess_abc123"
}
```

### Security Alerts (Redis JSON)
```json
{
  "user_id": "u001",
  "ip": "202.55.14.2",
  "score": 0.92,
  "location": "Sydney, AU",
  "geo_jump_km": 15000,
  "risk_factors": ["impossible_travel", "new_device"],
  "timestamp": 1691553792,
  "resolved": false
}
```

### User Behavior Vectors (Redis Vector Search)
```json
{
  "user_id": "u001",
  "timestamp": 1691553792,
  "embedding": [0.1, 0.2, 0.3, ...],
  "features": {
    "login_frequency": 0.8,
    "time_of_day": 0.6,
    "location_variance": 0.3
  }
}
```

## 🔒 Security Features

### Anomaly Detection
- **Geographic Impossibility**: Detects logins from geographically impossible locations
- **Velocity Analysis**: Identifies unusually fast travel between login locations
- **Behavioral Patterns**: ML-based detection of unusual user behavior
- **Time-based Analysis**: Detects logins at unusual times for specific users

### Threat Intelligence
- **IP Reputation**: Bloom filter-based checking of known malicious IPs
- **Device Fingerprinting**: Analysis of user agent strings and device characteristics
- **Session Analysis**: Detection of suspicious session patterns
- **Risk Scoring**: AI-powered risk assessment for each login attempt

## 📈 Monitoring & Observability

### Application Metrics
- Real-time event processing rate
- Alert generation frequency
- API response times
- Memory and CPU usage

### Redis Metrics
- Stream message processing lag
- TimeSeries data points stored
- Vector search query performance
- Bloom filter false positive rate

### Health Checks
- `/health` endpoint for application status
- Redis connectivity checks
- Container health monitoring
- Automated failover capabilities

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
uv run pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
docker compose -f compose.test.yml up --abort-on-container-exit
```

### Test Coverage

- Unit tests for core business logic
- Integration tests for Redis operations
- API endpoint testing
- Frontend component testing
- End-to-end scenario testing

## 🚀 Deployment

### Production Deployment

The application includes a complete CI/CD pipeline for AWS deployment:

1. **GitHub Actions** automatically builds and tests
2. **Docker images** are pushed to AWS ECR
3. **Infrastructure** is managed via AWS services
4. **Monitoring** is configured for production workloads

### Environment Variables

```bash
# Backend
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379
ENVIRONMENT=production

# Frontend
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.rediguard.com
NEXT_PUBLIC_API_BASE_URL=https://api.rediguard.com
```

### Docker Production Build

```bash
# Build production images
docker build -t rediguard-backend:prod ./backend
docker build -t rediguard-frontend:prod ./frontend

# Run production stack
docker compose -f compose.yml up -d
```

## 📚 Documentation

- [📋 Project Specification](./specification.md) - Detailed technical requirements
- [� Data Management Guide](./docs/DATA_MANAGEMENT.md) - Comprehensive data management features
- [☁️ AWS OIDC Setup](./docs/AWS_OIDC_SETUP.md) - Cloud deployment guide
- [🔄 CI/CD Setup](./docs/CICD_SETUP.md) - Pipeline configuration

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript/Python type hints
- Write tests for new features
- Update documentation as needed
- Ensure CI/CD pipeline passes
- Follow semantic commit conventions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Redis** team for the amazing Redis 8 features
- **FastAPI** for the excellent Python web framework
- **Next.js** team for the powerful React framework
- **Open source community** for the incredible tools and libraries

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ajitpdevops/rediguard/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ajitpdevops/rediguard/discussions)
- 📧 **Email**: ajitp.devops@gmail.com

---

<div align="center">
  <strong>Built with ❤️ using Redis 8, FastAPI, and Next.js</strong>
</div>