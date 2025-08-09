# Rediguard - Real-Time Security & Threat Detection MVP (Redis 8 + AI)

## Overview

This MVP demonstrates how Redis 8 features (Streams, TimeSeries, Vector Search, Bloom Filter, JSON, and Search/Aggregations) can be combined with AI to detect suspicious login events in real-time.

The MVP simulates login events, calculates anomaly scores with AI, stores results in Redis using advanced data structures, and surfaces alerts via Redis Search for a dashboard or API.

---

## Goals

- Real-time ingestion of simulated security events.
- AI-based anomaly detection (simple model: Isolation Forest or similar).
- Vector-based similarity checks for behavior patterns.
- Bloom filter checks for malicious IPs.
- Storage and querying of detailed alerts.

---

## Redis 8 Features Used

| Feature                 | Purpose                        | Example Use                                           |
| ----------------------- | ------------------------------ | ----------------------------------------------------- |
| **Streams**             | Real-time event ingestion      | Append login events for processing.                   |
| **TimeSeries**          | Historical trend tracking      | Track anomaly scores over time per user.              |
| **Vector Search**       | AI embedding similarity search | Compare current behavior vectors to historical norms. |
| **Bloom Filter**        | Fast blacklist checks          | Check if an IP is in the malicious IP list.           |
| **JSON**                | Rich alert storage             | Save all alert details in one JSON object.            |
| **Search/Aggregations** | Query & filter alerts          | Find alerts above a score threshold in time range.    |

---

## Data Model

### 1. **Login Events**

- **Key**: `logins:stream`
- **Type**: Redis Stream
- **Fields**:
  - `user_id` (string)
  - `ip` (string)
  - `location` (string, city or coordinates)
  - `timestamp` (UNIX epoch)

**Example Command**:

```bash
XADD logins:stream * user_id u001 ip 91.23.44.56 location "NY" timestamp 1691553792
```

---

### 2. **Anomaly Scores**

- **Key pattern**: `timeseries:{user_id}:anomaly`
- **Type**: Redis TimeSeries
- **Fields**:

  - `timestamp` (UNIX epoch)
  - `score` (float, 0–1)

**Example Command**:

```bash
TS.ADD timeseries:u001:anomaly 1691553792 0.92
```

---

### 3. **Behavior Embeddings**

- **Key**: `embeddings:index`
- **Type**: Redis Vector Search (HNSW index)
- **Schema**:

  - `user_id` (TEXT)
  - `timestamp` (NUMERIC)
  - `embedding` (VECTOR, FLOAT32, dim=N)

**Example Command**:

```bash
HSET embeddings:u001:1691553792 user_id "u001" timestamp 1691553792 embedding <binary_vector>
```

---

### 4. **Malicious IP Bloom Filter**

- **Key**: `bad_ips:bloom`
- **Type**: Redis Bloom Filter
- **Usage**:

  - Add known malicious IPs.
  - Check if an incoming IP is potentially bad.

**Example Commands**:

```bash
BF.ADD bad_ips:bloom 91.23.44.56
BF.EXISTS bad_ips:bloom 91.23.44.56
```

---

### 5. **Alert Documents**

- **Key pattern**: `alert:{user_id}:{timestamp}`
- **Type**: RedisJSON
- **Fields**:

  - `user_id` (string)
  - `ip` (string)
  - `score` (float)
  - `location` (string)
  - `geo_jump_km` (float, km between last login location and current)
  - `embedding` (array of floats)
  - `timestamp` (UNIX epoch)

**Example Command**:

```bash
JSON.SET alert:u001:1691553792 $ '{
  "user_id": "u001",
  "ip": "202.55.14.2",
  "score": 0.92,
  "location": "Sydney, AU",
  "geo_jump_km": 15000,
  "timestamp": 1691553792
}'
```

---

### 6. **Search Index for Alerts**

- **Index Name**: `alerts_idx`
- **Schema**:

  - `$.user_id` AS `user_id` TEXT
  - `$.ip` AS `ip` TEXT
  - `$.score` AS `score` NUMERIC
  - `$.location` AS `location` TEXT
  - `$.timestamp` AS `timestamp` NUMERIC

**Example Command**:

```bash
FT.CREATE alerts_idx ON JSON PREFIX 1 "alert:" SCHEMA \
  $.user_id AS user_id TEXT \
  $.ip AS ip TEXT \
  $.score AS score NUMERIC \
  $.location AS location TEXT \
  $.timestamp AS timestamp NUMERIC
```

---

## Processing Flow

1. **Ingest Events**

   - Login events pushed to `logins:stream`.

2. **AI Processing**

   - Worker reads from `logins:stream` via `XREADGROUP`.
   - Extracts features (login frequency, geo distance from last login, time-of-day).
   - Runs anomaly detection → outputs score.
   - Generates embedding vector.

3. **Store in Redis**

   - Append anomaly score to `timeseries:{user_id}:anomaly`.
   - Insert embedding into `embeddings:index`.
   - Check IP in `bad_ips:bloom`.

4. **Trigger Alert**

   - If score > 0.8 OR IP in Bloom filter:

     - Store JSON alert.
     - Indexed automatically for search.

5. **Query Alerts**

   - Fetch critical alerts:

     ```bash
     FT.SEARCH alerts_idx "@score:[0.8 +inf]"
     ```

   - Fetch last hour alerts:

     ```bash
     FT.SEARCH alerts_idx "@timestamp:[1691550000 1691553600]"
     ```

---

## Example Dataset

```json
[
  {
    "user_id": "u001",
    "ip": "91.23.44.56",
    "location": "New York, US",
    "timestamp": 1691553792
  },
  {
    "user_id": "u001",
    "ip": "202.55.14.2",
    "location": "Sydney, AU",
    "timestamp": 1691553930
  },
  {
    "user_id": "u002",
    "ip": "105.43.12.88",
    "location": "Berlin, DE",
    "timestamp": 1691554021
  }
]
```

---

## Key Patterns Summary

```
logins:stream                  # Redis Stream - login events
timeseries:{user_id}:anomaly   # Redis TimeSeries - anomaly scores
embeddings:{user_id}:{ts}      # Redis Vector Search entries
bad_ips:bloom                  # Redis Bloom Filter - malicious IPs
alert:{user_id}:{ts}           # RedisJSON - detailed alert
alerts_idx                     # Redis Search index for alerts
```

---

## Implementation Notes

- Use **Redis Stack 8** with all modules enabled.
- AI model can be a lightweight scikit-learn Isolation Forest or OpenAI embeddings for similarity search.
- All time values stored as UNIX epoch for easy range queries.
- Keep embedding dimension small (e.g., 128) for fast vector search in MVP.
- For demo purposes, data can be randomly generated but should include some obvious anomalies.

For this MVP, you’ve got **two good demo options** — both showing off Redis 8 + AI — but each has different strengths.

---

## UI-based demo (More visual, better for presentations)\*\*

**What it looks like:**

- Small web dashboard (FastAPI backend + Streamlit or simple React frontend).
- **Live Events Panel** → shows incoming login events (from Redis Streams).
- **Alerts Panel** → lists suspicious events in red, pulled from Redis Search.
- **User Timeline** → pulls TimeSeries anomaly scores to show graphs.
- **Vector Search** → “Find similar past events” button for a selected alert.
- **Bloom filter check** → instant “bad IP” badge next to event if matched.

**Pros**

- **Visual** — easier for investors/judges to understand.
- Feels like a “real” product.
- Lets you hide complexity but still talk about Redis features.
