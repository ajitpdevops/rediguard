# 🛡️ RediGuard - AI-Powered Real-Time Security & Threat Detection

[![CI/CD Pipeline](https://github.com/ajitpdevops/rediguard/actions/workflows/test.yml/badge.svg)](https://github.com/ajitpdevops/rediguard/actions)
[![Deploy to AWS](https://github.com/ajitpdevops/rediguard/actions/workflows/deploy.yml/badge.svg)](https://github.com/ajitpdevops/rediguard/actions)

A cutting-edge **AI-powered** real-time security monitoring and threat detection system powered by **Redis 8** and **Large Language Models**. RediGuard combines advanced Redis data structures with machine learning and conversational AI to detect suspicious login patterns, anomalous behaviors, and potential security threats in real-time, while providing intelligent threat explanations and interactive security insights.

## 🎯 Overview

RediGuard demonstrates how Redis 8's powerful features can be leveraged for AI-enhanced cybersecurity applications:

- **Real-time event processing** using Redis Streams
- **AI-powered anomaly detection** with vector similarity search
- **LLM-powered threat explanations** with conversational AI interface
- **Intelligent security assistant** with contextual awareness
- **Time-series analysis** for pattern recognition
- **Bloom filters** for efficient blacklist checking
- **JSON storage** for complex alert data
- **Full-text search** for alert querying and analysis

## ✨ Features

### 🤖 AI-Powered Security Intelligence
- **LLM-powered threat explanations** with business-friendly language using llama3-8b-8192
- **Conversational security assistant** with contextual system awareness and chat interface
- **Real-time threat analysis** integrated directly into alert cards with risk assessment
- **Interactive AI chat interface** for security insights, investigation, and guidance
- **Intelligent threat summarization** with natural language risk assessment and recommendations
- **Vector embeddings** for behavioral pattern analysis and anomaly detection
- **Semantic caching** for optimized LLM response times and cost efficiency

### 🔒 Advanced Security Monitoring
- **Real-time login event ingestion** and processing with Redis Streams
- **Geolocation-based anomaly detection** for impossible travel scenarios
- **IP address reputation checking** via Redis Bloom filters for efficient lookups
- **User behavior pattern analysis** using AI embeddings and vector similarity search
- **ML-powered anomaly detection** with Isolation Forest algorithms and time-series analysis
- **Event correlation** and pattern recognition across multiple data dimensions
- **Automated threat scoring** with configurable risk thresholds and alerting
- **Event prioritization system** with high/medium/low priority classification
- **Security-focused UI** with toggle for forensic analysis mode

### 📊 Analytics & Insights
- Interactive dashboard with real-time updates
- Historical trend analysis with time-series data
- Advanced search and filtering of security alerts
- Visual representation of threat landscapes
- AI-enhanced security metrics and recommendations

### 🚀 Performance & Scalability
- Redis 8 powered for sub-millisecond response times
- Containerized architecture for easy deployment
- Horizontal scaling capabilities
- CI/CD pipeline for automated testing and deployment
- LLM response caching for optimized AI performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Redis 8     │    │   LLM Service   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (All Modules) │◄──►│   (Groq API)    │
│                 │    │                 │    │                 │    │                 │
│ - Dashboard     │    │ - API Routes    │    │ - Streams       │    │ - Threat Analysis│
│ - Real-time UI  │    │ - AI Processing │    │ - TimeSeries    │    │ - Chat Interface│
│ - AI Assistant  │    │ - Event Workers │    │ - Vector Search │    │ - Explanations  │
│ - Chat Interface│    │ - LLM Service   │    │ - Bloom Filters │    │ - Risk Assessment│
│ - Charts        │    │ - Threat Analysis│   │ - JSON Documents│    │ - Recommendations│
└─────────────────┘    └─────────────────┘    │ - Search Index  │    └─────────────────┘
                                              └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **🐍 Python 3.10+** with FastAPI framework
- **⚡ uv** for dependency management and Python execution
- **🔄 Async/await** for high-performance operations
- **🤖 Groq API** with llama3-8b-8192 for AI-powered threat analysis
- **💬 LLM Service** for conversational security assistance

### Frontend  
- **⚛️ Next.js 15** with React Server Components
- **📘 TypeScript** for type-safe development
- **🎨 Tailwind CSS** for styling
- **🌙 shadcn/ui** components
- **🔄 Real-time updates** via API polling
- **🤖 AI Assistant** interface for threat investigation

### Redis Stack (8.2-rc1)
- **🏄‍♂️ Redis Streams** - Event streaming and processing
- **📊 RedisTimeSeries** - Time-based anomaly tracking and analytics
- **🔍 RediSearch** - Vector similarity search with HNSW algorithm
- **📄 RedisJSON** - Document storage for complex security events
- **🌸 RedisBloom** - Probabilistic data structures for deduplication
- **⚡ Redis Core** - High-performance caching and session management

### Infrastructure
- **🐳 Docker & Docker Compose** for development environment
- **🌐 uvicorn** ASGI server
- **📋 Structured logging** with Python logging module

### Key Dependencies

#### Backend (Python)
- **FastAPI** - Modern, fast web framework for building APIs
- **Redis** - Redis client for Python with async support
- **groq** - Groq API client for LLM integration
- **httpx** - Async HTTP client for API calls
- **scikit-learn** - Machine learning library for anomaly detection
- **numpy** - Numerical computing for data processing
- **uvicorn** - Lightning-fast ASGI server

#### Frontend (Node.js)
- **Next.js 15** - React framework with server components
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **Recharts** - Composable charting library
- **shadcn/ui** - Modern UI component library

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

## 🤖 AI & LLM Integration

### **AI-Powered Threat Analysis**
- **Intelligent explanations** for detected anomalies and threats
- **Conversational interface** for security investigation
- **Risk assessment** with natural language descriptions
- **Proactive recommendations** for threat mitigation

### **AI Assistant Endpoints**

```bash
# Get threat explanation for a specific event
curl -X POST "http://localhost:8000/api/v1/llm/explain-threat" \
  -H "Content-Type: application/json" \
  -d '{"event_id": "event_123"}'

# Chat with AI assistant about security
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the current security risks?", "session_id": "session_123"}'

# Get system health assessment
curl -X GET "http://localhost:8000/api/v1/llm/health-assessment"
```

### **LLM Configuration**
- **Model**: llama3-8b-8192 via Groq API
- **Response time**: Sub-second latency for threat analysis
- **Context awareness**: Integrated with Redis event data
- **Semantic caching**: Optimized for repeated queries

## 🔍 Event Prioritization System

RediGuard implements an intelligent event prioritization system that categorizes security events based on their potential impact and relevance to security operations:

### **High Priority Events (Always Shown)**
- **Failed authentication attempts** - Direct security threats requiring immediate attention
- **Privilege escalation attempts** - Critical security violations
- **Unusual data access patterns** - Potential data exfiltration attempts
- **Geographic anomalies** - Impossible travel scenarios and location-based threats
- **Time-based anomalies** - Off-hours access and unusual timing patterns
- **API abuse patterns** - Potential automated attacks and rate limit violations

### **Medium Priority Events (Contextual Relevance)**
- **Successful logins with risk factors** - Authentication events that contribute to behavioral patterns
- **Normal API calls with elevated risk** - API usage for baseline establishment and pattern analysis
- **Administrative actions** - All admin activities due to their inherently sensitive nature
- **Password changes and security updates** - Account security modifications

### **Low Priority Events (Background Processing)**
- **Routine user activity** - Normal application usage for baseline establishment
- **Normal application events** - Standard system operations
- **System maintenance events** - Automated system processes

### **UI Toggle Features**
- **Security Events View**: Default view showing high and medium priority events for operational focus
- **All Events View**: Forensic analysis mode with pagination and lazy loading for detailed investigation
- **Smart Pagination**: Prevents UI hangs by limiting data loads and implementing efficient navigation

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

### AI & LLM Endpoints

- `POST /api/v1/llm/explain-threat` - Get AI-powered threat explanation
- `POST /api/v1/llm/chat` - Chat with AI security assistant
- `GET /api/v1/llm/health-assessment` - Get system health assessment
- `POST /api/v1/llm/analyze-event` - Deep analysis of security events

### Event Endpoints

- `GET /api/v1/events/security` - Get security-focused events (high/medium priority)
- `GET /api/v1/events/all` - Get all events including low priority for forensic analysis
- `GET /api/v1/alerts/search` - Search security alerts with filters
- `GET /api/v1/users/{user_id}/anomaly-history` - User anomaly history
- `GET /api/v1/users/{user_id}/similar-behavior` - Similar behavior patterns

### Data Management Endpoints

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

Required environment variables for full functionality:

```bash
# LLM Service Configuration (Required for AI features)
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-8b-8192
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.1

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password
ENVIRONMENT=production

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# Frontend Configuration
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.rediguard.com
NEXT_PUBLIC_API_BASE_URL=https://api.rediguard.com
```

**Important**: Create a `.env` file in the backend directory with these variables. The Groq API key is required for all AI-powered features including threat explanations and chat interface.

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

## 🚧 Current Status & Roadmap

### ✅ **Completed Features**
- **Core Security Monitoring**: Real-time event ingestion, anomaly detection, threat scoring
- **Redis 8 Integration**: Streams, TimeSeries, RediSearch, JSON, Bloom filters
- **AI-Powered Analysis**: LLM threat explanations, conversational assistant, vector embeddings
- **Modern Frontend**: Next.js 15 dashboard with real-time updates and AI chat interface
- **Data Management**: Automated seeding, streaming, and comprehensive statistics
- **Development Environment**: Docker Compose setup with hot reloading

### 🔄 **In Progress**
- **Advanced ML Models**: Enhanced anomaly detection algorithms
- **Performance Optimization**: Response time improvements and caching strategies
- **Extended AI Features**: Multi-turn conversations and advanced threat correlation

### 📋 **Planned Features**
- **Authentication & Authorization**: User management and role-based access control
- **Alert Management**: Email/SMS notifications and escalation workflows
- **Advanced Visualizations**: Network topology views and threat heat maps
- **Integration APIs**: SIEM connectors and third-party security tool integration
- **Mobile Application**: React Native app for on-the-go security monitoring
- **Multi-tenant Support**: Enterprise-ready isolation and data segregation
- **Compliance Reporting**: Automated security compliance reports and auditing

### 🔍 **Missing Components (Technical Debt)**
- **Comprehensive Test Suite**: Unit, integration, and end-to-end testing
- **Production Security**: Rate limiting, input validation, and security headers
- **Monitoring & Observability**: Application metrics, health checks, and alerting
- **Documentation**: API documentation, deployment guides, and troubleshooting
- **Error Handling**: Graceful degradation and user-friendly error messages
- **Configuration Management**: Environment-specific settings and secrets management

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