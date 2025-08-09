"""Redis Stack client with all Redis 8 modules enabled"""

import redis
import json
import numpy as np
from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisStackClient:
    """Enhanced Redis client with full Redis Stack 8 features"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._is_connected = False
        self._modules_available = {
            'search': False,
            'timeseries': False,
            'json': False,
            'bloom': False,
            'graph': False
        }
    
    def connect(self) -> redis.Redis:
        """Connect to Redis Stack"""
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=False,  # Keep as bytes for binary data
                health_check_interval=30
            )
            
            # Test connection
            self._client.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis Stack at {settings.redis_host}:{settings.redis_port}")
            
            # Check available modules
            self._check_modules()
            
            # Initialize Redis Stack features
            self._initialize_stack_features()
            
            return self._client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis Stack: {e}")
            raise
    
    def _check_modules(self):
        """Check which Redis modules are available"""
        if not self._client:
            return
            
        try:
            modules = self._client.execute_command("MODULE", "LIST")
            available_modules = []
            
            for module_info in modules:
                if isinstance(module_info, list) and len(module_info) >= 2:
                    module_name = module_info[1].decode() if isinstance(module_info[1], bytes) else module_info[1]
                    available_modules.append(module_name.lower())
            
            # Check for specific modules
            self._modules_available['search'] = any('search' in mod for mod in available_modules)
            self._modules_available['timeseries'] = any('timeseries' in mod for mod in available_modules)
            self._modules_available['json'] = any('json' in mod or 'rejson' in mod for mod in available_modules)
            self._modules_available['bloom'] = any('bloom' in mod for mod in available_modules)
            
            logger.info(f"Available Redis modules: {self._modules_available}")
            
        except Exception as e:
            logger.warning(f"Could not check Redis modules: {e}")
    
    def _exec(self, *args):
        """Execute Redis command with proper error handling"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return self._client.execute_command(*args)
    
    def _initialize_stack_features(self):
        """Initialize all Redis Stack features"""
        try:
            # Create TimeSeries for anomaly scores
            self._initialize_timeseries()
            
            # Create Search indexes
            self._initialize_search_indexes()
            
            # Initialize Bloom filters
            self._initialize_bloom_filters()
            
            # Test JSON operations
            self._initialize_json_features()
            
            logger.info("Redis Stack features initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Redis Stack features: {e}")
    
    def _initialize_timeseries(self):
        """Initialize Redis TimeSeries for anomaly tracking"""
        if not self._modules_available['timeseries']:
            logger.warning("TimeSeries module not available")
            return
        
        try:
            # Create sample time series for demo users
            demo_users = ['alice', 'bob', 'charlie', 'diana']
            
            for user in demo_users:
                ts_key = f"timeseries:{user}:anomaly"
                try:
                    # Try to create the time series
                    self._exec(
                        "TS.CREATE", ts_key,
                        "RETENTION", 86400000,  # 24 hours in milliseconds
                        "LABELS", "user", user, "metric", "anomaly_score"
                    )
                    logger.debug(f"Created TimeSeries for user {user}")
                except Exception as e:
                    if "TSDB: key already exists" not in str(e):
                        logger.warning(f"Could not create TimeSeries for {user}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TimeSeries: {e}")
    
    def _initialize_search_indexes(self):
        """Initialize Redis Search indexes"""
        if not self._modules_available['search']:
            logger.warning("Search module not available")
            return
        
        try:
            # Create alerts index
            self._create_alerts_search_index()
            
            # Create embeddings vector index  
            self._create_embeddings_vector_index()
            
        except Exception as e:
            logger.error(f"Failed to initialize Search indexes: {e}")
    
    def _create_alerts_search_index(self):
        """Create search index for security alerts"""
        try:
            # Check if index exists
            try:
                self._exec("FT.INFO", "alerts_idx")
                logger.info("Alerts search index already exists")
                return
            except:
                pass  # Index doesn't exist, create it
            
            # Create the index with JSON schema
            self._exec(
                "FT.CREATE", "alerts_idx",
                "ON", "JSON",
                "PREFIX", "1", "alert:",
                "SCHEMA",
                "$.user_id", "AS", "user_id", "TEXT",
                "$.ip", "AS", "ip", "TEXT", 
                "$.score", "AS", "score", "NUMERIC",
                "$.location", "AS", "location", "TEXT",
                "$.timestamp", "AS", "timestamp", "NUMERIC",
                "$.geo_jump_km", "AS", "geo_jump_km", "NUMERIC",
                "$.is_malicious_ip", "AS", "is_malicious_ip", "TAG"
            )
            
            logger.info("Created alerts search index")
            
        except Exception as e:
            logger.error(f"Failed to create alerts search index: {e}")
    
    def _create_embeddings_vector_index(self):
        """Create vector search index for behavior embeddings"""
        try:
            # Check if index exists
            try:
                self._exec("FT.INFO", "embeddings_idx")
                logger.info("Embeddings vector index already exists")
                return
            except:
                pass  # Index doesn't exist, create it
            
            # Create vector index
            self._exec(
                "FT.CREATE", "embeddings_idx",
                "ON", "HASH",
                "PREFIX", "1", "embeddings:",
                "SCHEMA",
                "user_id", "TEXT",
                "timestamp", "NUMERIC",
                "embedding", "VECTOR", "HNSW", "6", 
                "TYPE", "FLOAT32", 
                "DIM", str(settings.vector_dimension),
                "DISTANCE_METRIC", "COSINE"
            )
            
            logger.info("Created embeddings vector index")
            
        except Exception as e:
            logger.error(f"Failed to create embeddings vector index: {e}")
    
    def _initialize_bloom_filters(self):
        """Initialize Bloom filters for malicious IPs"""
        if not self._modules_available['bloom']:
            logger.warning("Bloom module not available")
            return
        
        try:
            bloom_key = "bad_ips:bloom"
            
            # Check if bloom filter exists
            try:
                self._exec("BF.INFO", bloom_key)
                logger.info("Bloom filter already exists")
                return
            except:
                pass  # Bloom filter doesn't exist, create it
            
            # Create bloom filter with 1% error rate, 10000 initial capacity
            self._exec("BF.RESERVE", bloom_key, 0.01, 10000)
            
            # Add sample malicious IPs
            malicious_ips = [
                "192.168.1.100", "10.0.0.50", "203.0.113.1", "198.51.100.1",
                "185.220.101.1", "91.203.5.165", "45.95.147.228", "89.248.171.75"
            ]
            
            for ip in malicious_ips:
                self._exec("BF.ADD", bloom_key, ip)
            
            logger.info(f"Created and populated bloom filter with {len(malicious_ips)} malicious IPs")
            
        except Exception as e:
            logger.error(f"Failed to initialize bloom filter: {e}")
    
    def _initialize_json_features(self):
        """Initialize and test JSON features"""
        if not self._modules_available['json']:
            logger.warning("JSON module not available")
            return
        
        try:
            # Test JSON.SET operation
            test_key = "test:json:config"
            test_data = {
                "system": "rediguard",
                "version": "1.0.0",
                "features": ["timeseries", "search", "bloom", "json"],
                "initialized_at": datetime.now().isoformat()
            }
            
            self._exec("JSON.SET", test_key, "$", json.dumps(test_data))
            logger.info("JSON features initialized and tested")
            
        except Exception as e:
            logger.error(f"Failed to initialize JSON features: {e}")
    
    @property
    def client(self):
        """Get Redis client"""
        if not self._client or not self._is_connected:
            return self.connect()
        return self._client
    
    def close(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("Redis Stack connection closed")
    
    # ===== REDIS STREAMS OPERATIONS =====
    
    def add_login_event(self, user_id: str, ip: str, location: str, timestamp: Optional[int] = None) -> str:
        """Add login event to Redis Stream"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
            
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        
        try:
            stream_id = self._client.xadd(
                "logins:stream",
                {
                    "user_id": user_id,
                    "ip": ip,
                    "location": location,
                    "timestamp": str(timestamp)
                },
                maxlen=settings.redis_stream_maxlen
            )
            
            return stream_id.decode() if isinstance(stream_id, bytes) else stream_id
            
        except Exception as e:
            logger.error(f"Failed to add login event: {e}")
            raise
    
    def read_login_events(self, consumer_group: str, consumer_name: str, count: int = 10) -> List[Dict]:
        """Read login events from stream using consumer group"""
        if not self._client:
            return []
            
        try:
            # Create consumer group if it doesn't exist
            try:
                self._client.xgroup_create("logins:stream", consumer_group, id="0", mkstream=True)
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.error(f"Failed to create consumer group: {e}")
            
            # Read messages
            messages = self._client.xreadgroup(
                consumer_group,
                consumer_name,
                {"logins:stream": ">"},
                count=count,
                block=1000
            )
            
            events = []
            for stream_name, stream_messages in messages:
                for message_id, fields in stream_messages:
                    # Decode fields
                    decoded_fields = {}
                    for key, value in fields.items():
                        key_str = key.decode() if isinstance(key, bytes) else key
                        value_str = value.decode() if isinstance(value, bytes) else value
                        decoded_fields[key_str] = value_str
                    
                    events.append({
                        "message_id": message_id.decode() if isinstance(message_id, bytes) else message_id,
                        "fields": decoded_fields
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to read login events: {e}")
            return []
    
    def ack_login_event(self, consumer_group: str, message_id: str):
        """Acknowledge processed login event"""
        if not self._client:
            return
            
        try:
            self._client.xack("logins:stream", consumer_group, message_id)
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
    
    # ===== REDIS TIMESERIES OPERATIONS =====
    
    def add_anomaly_score(self, user_id: str, score: float, timestamp: Optional[int] = None) -> bool:
        """Add anomaly score to user's TimeSeries"""
        if not self._modules_available['timeseries']:
            logger.warning("TimeSeries not available, using fallback")
            return self._add_anomaly_score_fallback(user_id, score, timestamp)
        
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        
        try:
            ts_key = f"timeseries:{user_id}:anomaly"
            
            # Create time series if it doesn't exist
            try:
                self._exec(
                    "TS.CREATE", ts_key,
                    "RETENTION", 86400000,  # 24 hours
                    "LABELS", "user", user_id, "metric", "anomaly_score"
                )
            except Exception as e:
                if "TSDB: key already exists" not in str(e):
                    logger.warning(f"Could not create TimeSeries: {e}")
            
            # Add data point (timestamp in milliseconds)
            self._exec("TS.ADD", ts_key, timestamp * 1000, score)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add anomaly score: {e}")
            return False
    
    def get_anomaly_scores(self, user_id: str, hours: int = 24) -> List[tuple]:
        """Get user's anomaly scores from TimeSeries"""
        if not self._modules_available['timeseries']:
            return self._get_anomaly_scores_fallback(user_id, hours)
        
        try:
            ts_key = f"timeseries:{user_id}:anomaly"
            
            # Calculate time range in milliseconds
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (hours * 3600 * 1000)
            
            # Get time series data
            result = self._exec("TS.RANGE", ts_key, start_time, end_time)
            
            # Convert to list of (timestamp, score) tuples
            scores = []
            for timestamp_ms, score_bytes in result:
                timestamp = int(timestamp_ms) // 1000  # Convert back to seconds
                score = float(score_bytes)
                scores.append((timestamp, score))
            
            return scores
            
        except Exception as e:
            logger.error(f"Failed to get anomaly scores: {e}")
            return []
    
    # ===== REDIS JSON OPERATIONS =====
    
    def store_alert_json(self, alert_id: str, alert_data: Dict) -> bool:
        """Store security alert as JSON document"""
        if not self._modules_available['json']:
            return self._store_alert_fallback(alert_id, alert_data)
        
        try:
            key = f"alert:{alert_id}"
            self._exec("JSON.SET", key, "$", json.dumps(alert_data))
            return True
            
        except Exception as e:
            logger.error(f"Failed to store alert JSON: {e}")
            return False
    
    def get_alert_json(self, alert_id: str) -> Optional[Dict]:
        """Get security alert JSON document"""
        if not self._modules_available['json']:
            return self._get_alert_fallback(alert_id)
        
        try:
            key = f"alert:{alert_id}"
            result = self._exec("JSON.GET", key)
            
            if result:
                json_str = result.decode() if isinstance(result, bytes) else result
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get alert JSON: {e}")
            return None
    
    # ===== REDIS SEARCH OPERATIONS =====
    
    def search_alerts(self, query: str, limit: int = 100) -> List[Dict]:
        """Search alerts using RediSearch"""
        if not self._modules_available['search']:
            return self._search_alerts_fallback(query, limit)
        
        try:
            result = self._exec(
                "FT.SEARCH", "alerts_idx", query,
                "LIMIT", "0", str(limit)
            )
            
            alerts = []
            # Parse search results (skip count at index 0)
            for i in range(1, len(result), 2):
                doc_id = result[i].decode() if isinstance(result[i], bytes) else result[i]
                
                # Get the JSON document
                alert_data = self.get_alert_json(doc_id.replace("alert:", ""))
                if alert_data:
                    alerts.append(alert_data)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to search alerts: {e}")
            return []
    
    # ===== REDIS BLOOM FILTER OPERATIONS =====
    
    def check_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in malicious IP bloom filter"""
        if not self._modules_available['bloom']:
            return self._check_malicious_ip_fallback(ip)
        
        try:
            result = self._exec("BF.EXISTS", "bad_ips:bloom", ip)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to check malicious IP: {e}")
            return False
    
    def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP bloom filter"""
        if not self._modules_available['bloom']:
            return self._add_malicious_ip_fallback(ip)
        
        try:
            result = self._exec("BF.ADD", "bad_ips:bloom", ip)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to add malicious IP: {e}")
            return False
    
    # ===== VECTOR SEARCH OPERATIONS =====
    
    def store_embedding(self, user_id: str, timestamp: int, embedding: List[float]) -> bool:
        """Store behavior embedding for vector search"""
        if not self._modules_available['search']:
            return self._store_embedding_fallback(user_id, timestamp, embedding)
        
        if not self._client:
            return False
            
        try:
            key = f"embeddings:{user_id}:{timestamp}"
            
            # Convert embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            # Store in hash for vector search
            self._client.hset(key, mapping={
                "user_id": user_id,
                "timestamp": str(timestamp),
                "embedding": embedding_bytes
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False
    
    def vector_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Perform vector similarity search"""
        if not self._modules_available['search']:
            return self._vector_search_fallback(query_embedding, limit)
        
        try:
            # Convert query embedding to bytes
            query_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
            
            # Perform KNN search
            result = self._exec(
                "FT.SEARCH", "embeddings_idx",
                f"*=>[KNN {limit} @embedding $query_vector AS distance]",
                "PARAMS", "2", "query_vector", query_bytes,
                "SORTBY", "distance",
                "DIALECT", "2"
            )
            
            similar_embeddings = []
            # Parse results
            for i in range(1, len(result), 2):
                doc_id = result[i].decode() if isinstance(result[i], bytes) else result[i]
                doc_data = result[i + 1]
                
                # Parse document data
                embedding_data = {}
                for j in range(0, len(doc_data), 2):
                    field = doc_data[j].decode() if isinstance(doc_data[j], bytes) else doc_data[j]
                    value = doc_data[j + 1]
                    
                    if field == "distance":
                        embedding_data[field] = float(value)
                    elif field in ["user_id", "timestamp"]:
                        embedding_data[field] = value.decode() if isinstance(value, bytes) else value
                
                similar_embeddings.append(embedding_data)
            
            return similar_embeddings
            
        except Exception as e:
            logger.error(f"Failed to perform vector search: {e}")
            return []
    
    # ===== FALLBACK METHODS (for when modules are not available) =====
    
    def _add_anomaly_score_fallback(self, user_id: str, score: float, timestamp: Optional[int]) -> bool:
        """Fallback method using sorted sets"""
        if not self._client:
            return False
            
        try:
            key = f"timeseries:{user_id}:anomaly"
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            self._client.zadd(key, {str(score): timestamp})
            
            # Keep only recent data
            cutoff = timestamp - (24 * 3600)
            self._client.zremrangebyscore(key, 0, cutoff)
            
            return True
        except Exception as e:
            logger.error(f"Fallback anomaly score storage failed: {e}")
            return False
    
    def _get_anomaly_scores_fallback(self, user_id: str, hours: int) -> List[tuple]:
        """Fallback method using sorted sets"""
        if not self._client:
            return []
            
        try:
            key = f"timeseries:{user_id}:anomaly"
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            result = self._client.zrangebyscore(key, start_time, end_time, withscores=True)
            return [(int(score), float(value)) for value, score in result]
        except Exception as e:
            logger.error(f"Fallback anomaly score retrieval failed: {e}")
            return []
    
    def _store_alert_fallback(self, alert_id: str, alert_data: Dict) -> bool:
        """Fallback using regular Redis string"""
        if not self._client:
            return False
            
        try:
            key = f"alert:{alert_id}"
            self._client.set(key, json.dumps(alert_data))
            return True
        except Exception as e:
            logger.error(f"Fallback alert storage failed: {e}")
            return False
    
    def _get_alert_fallback(self, alert_id: str) -> Optional[Dict]:
        """Fallback using regular Redis string"""
        if not self._client:
            return None
            
        try:
            key = f"alert:{alert_id}"
            result = self._client.get(key)
            if result:
                json_str = result.decode() if isinstance(result, bytes) else result
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Fallback alert retrieval failed: {e}")
            return None
    
    def _search_alerts_fallback(self, query: str, limit: int) -> List[Dict]:
        """Fallback using key pattern matching"""
        if not self._client:
            return []
            
        try:
            keys = self._client.keys("alert:*")
            alerts = []
            
            for key in keys[:limit]:
                key_str = key.decode() if isinstance(key, bytes) else key
                alert_id = key_str.replace("alert:", "")
                alert_data = self._get_alert_fallback(alert_id)
                if alert_data:
                    alerts.append(alert_data)
            
            return alerts
        except Exception as e:
            logger.error(f"Fallback alert search failed: {e}")
            return []
    
    def _check_malicious_ip_fallback(self, ip: str) -> bool:
        """Fallback using Redis set"""
        if not self._client:
            return False
            
        try:
            return bool(self._client.sismember("bad_ips:set", ip))
        except Exception as e:
            logger.error(f"Fallback IP check failed: {e}")
            return False
    
    def _add_malicious_ip_fallback(self, ip: str) -> bool:
        """Fallback using Redis set"""
        if not self._client:
            return False
            
        try:
            return bool(self._client.sadd("bad_ips:set", ip))
        except Exception as e:
            logger.error(f"Fallback IP addition failed: {e}")
            return False
    
    def _store_embedding_fallback(self, user_id: str, timestamp: int, embedding: List[float]) -> bool:
        """Fallback using hash"""
        if not self._client:
            return False
            
        try:
            key = f"embeddings:{user_id}:{timestamp}"
            self._client.hset(key, mapping={
                "user_id": user_id,
                "timestamp": str(timestamp),
                "embedding": json.dumps(embedding)
            })
            return True
        except Exception as e:
            logger.error(f"Fallback embedding storage failed: {e}")
            return False
    
    def _vector_search_fallback(self, query_embedding: List[float], limit: int) -> List[Dict]:
        """Fallback using cosine similarity"""
        if not self._client:
            return []
            
        try:
            keys = self._client.keys("embeddings:*")
            similarities = []
            
            for key in keys[:100]:  # Limit for performance
                try:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    data = self._client.hgetall(key_str)
                    
                    if b'embedding' in data:
                        stored_embedding = json.loads(data[b'embedding'].decode())
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)
                        
                        similarities.append({
                            'user_id': data[b'user_id'].decode(),
                            'timestamp': data[b'timestamp'].decode(),
                            'distance': 1 - similarity
                        })
                except:
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['distance'])
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Fallback vector search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        try:
            import math
            
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            if not vec1 or not vec2:
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception:
            return 0.0


# Global Redis Stack client instance
redis_stack_client = RedisStackClient()
    
    def _initialize_stack_features(self):
        """Initialize all Redis Stack features"""
        try:
            # Create TimeSeries for anomaly scores
            self._initialize_timeseries()
            
            # Create Search indexes
            self._initialize_search_indexes()
            
            # Initialize Bloom filters
            self._initialize_bloom_filters()
            
            # Test JSON operations
            self._initialize_json_features()
            
            logger.info("Redis Stack features initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Redis Stack features: {e}")
    
    def _initialize_timeseries(self):
        """Initialize Redis TimeSeries for anomaly tracking"""
        if not self._modules_available['timeseries']:
            logger.warning("TimeSeries module not available")
            return
        
        try:
            # Create sample time series for demo users
            demo_users = ['alice', 'bob', 'charlie', 'diana']
            
            for user in demo_users:
                ts_key = f"timeseries:{user}:anomaly"
                try:
                    # Try to create the time series
                    self._client.execute_command(
                        "TS.CREATE", ts_key,
                        "RETENTION", 86400000,  # 24 hours in milliseconds
                        "LABELS", "user", user, "metric", "anomaly_score"
                    )
                    logger.debug(f"Created TimeSeries for user {user}")
                except Exception as e:
                    if "TSDB: key already exists" not in str(e):
                        logger.warning(f"Could not create TimeSeries for {user}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TimeSeries: {e}")
    
    def _initialize_search_indexes(self):
        """Initialize Redis Search indexes"""
        if not self._modules_available['search']:
            logger.warning("Search module not available")
            return
        
        try:
            # Create alerts index
            self._create_alerts_search_index()
            
            # Create embeddings vector index  
            self._create_embeddings_vector_index()
            
        except Exception as e:
            logger.error(f"Failed to initialize Search indexes: {e}")
    
    def _create_alerts_search_index(self):
        """Create search index for security alerts"""
        try:
            # Check if index exists
            try:
                self._client.execute_command("FT.INFO", "alerts_idx")
                logger.info("Alerts search index already exists")
                return
            except:
                pass  # Index doesn't exist, create it
            
            # Create the index with JSON schema
            self._client.execute_command(
                "FT.CREATE", "alerts_idx",
                "ON", "JSON",
                "PREFIX", "1", "alert:",
                "SCHEMA",
                "$.user_id", "AS", "user_id", "TEXT",
                "$.ip", "AS", "ip", "TEXT", 
                "$.score", "AS", "score", "NUMERIC",
                "$.location", "AS", "location", "TEXT",
                "$.timestamp", "AS", "timestamp", "NUMERIC",
                "$.geo_jump_km", "AS", "geo_jump_km", "NUMERIC",
                "$.is_malicious_ip", "AS", "is_malicious_ip", "TAG"
            )
            
            logger.info("Created alerts search index")
            
        except Exception as e:
            logger.error(f"Failed to create alerts search index: {e}")
    
    def _create_embeddings_vector_index(self):
        """Create vector search index for behavior embeddings"""
        try:
            # Check if index exists
            try:
                self._client.execute_command("FT.INFO", "embeddings_idx")
                logger.info("Embeddings vector index already exists")
                return
            except:
                pass  # Index doesn't exist, create it
            
            # Create vector index
            self._client.execute_command(
                "FT.CREATE", "embeddings_idx",
                "ON", "HASH",
                "PREFIX", "1", "embeddings:",
                "SCHEMA",
                "user_id", "TEXT",
                "timestamp", "NUMERIC",
                "embedding", "VECTOR", "HNSW", "6", 
                "TYPE", "FLOAT32", 
                "DIM", str(settings.vector_dimension),
                "DISTANCE_METRIC", "COSINE"
            )
            
            logger.info("Created embeddings vector index")
            
        except Exception as e:
            logger.error(f"Failed to create embeddings vector index: {e}")
    
    def _initialize_bloom_filters(self):
        """Initialize Bloom filters for malicious IPs"""
        if not self._modules_available['bloom']:
            logger.warning("Bloom module not available")
            return
        
        try:
            bloom_key = "bad_ips:bloom"
            
            # Check if bloom filter exists
            try:
                self._client.execute_command("BF.INFO", bloom_key)
                logger.info("Bloom filter already exists")
                return
            except:
                pass  # Bloom filter doesn't exist, create it
            
            # Create bloom filter with 1% error rate, 10000 initial capacity
            self._client.execute_command("BF.RESERVE", bloom_key, 0.01, 10000)
            
            # Add sample malicious IPs
            malicious_ips = [
                "192.168.1.100", "10.0.0.50", "203.0.113.1", "198.51.100.1",
                "185.220.101.1", "91.203.5.165", "45.95.147.228", "89.248.171.75"
            ]
            
            for ip in malicious_ips:
                self._client.execute_command("BF.ADD", bloom_key, ip)
            
            logger.info(f"Created and populated bloom filter with {len(malicious_ips)} malicious IPs")
            
        except Exception as e:
            logger.error(f"Failed to initialize bloom filter: {e}")
    
    def _initialize_json_features(self):
        """Initialize and test JSON features"""
        if not self._modules_available['json']:
            logger.warning("JSON module not available")
            return
        
        try:
            # Test JSON.SET operation
            test_key = "test:json:config"
            test_data = {
                "system": "rediguard",
                "version": "1.0.0",
                "features": ["timeseries", "search", "bloom", "json"],
                "initialized_at": datetime.now().isoformat()
            }
            
            self._client.execute_command("JSON.SET", test_key, "$", json.dumps(test_data))
            logger.info("JSON features initialized and tested")
            
        except Exception as e:
            logger.error(f"Failed to initialize JSON features: {e}")
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client"""
        if not self._client or not self._is_connected:
            return self.connect()
        return self._client
    
    def close(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("Redis Stack connection closed")
    
    # ===== REDIS STREAMS OPERATIONS =====
    
    def add_login_event(self, user_id: str, ip: str, location: str, timestamp: Optional[int] = None) -> str:
        """Add login event to Redis Stream"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
            
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        
        try:
            stream_id = self._client.xadd(
                "logins:stream",
                {
                    "user_id": user_id,
                    "ip": ip,
                    "location": location,
                    "timestamp": str(timestamp)
                },
                maxlen=settings.redis_stream_maxlen
            )
            
            return stream_id.decode() if isinstance(stream_id, bytes) else stream_id
            
        except Exception as e:
            logger.error(f"Failed to add login event: {e}")
            raise
    
    def read_login_events(self, consumer_group: str, consumer_name: str, count: int = 10) -> List[Dict]:
        """Read login events from stream using consumer group"""
        try:
            # Create consumer group if it doesn't exist
            try:
                self._client.xgroup_create("logins:stream", consumer_group, id="0", mkstream=True)
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.error(f"Failed to create consumer group: {e}")
            
            # Read messages
            messages = self._client.xreadgroup(
                consumer_group,
                consumer_name,
                {"logins:stream": ">"},
                count=count,
                block=1000
            )
            
            events = []
            for stream_name, stream_messages in messages:
                for message_id, fields in stream_messages:
                    # Decode fields
                    decoded_fields = {}
                    for key, value in fields.items():
                        key_str = key.decode() if isinstance(key, bytes) else key
                        value_str = value.decode() if isinstance(value, bytes) else value
                        decoded_fields[key_str] = value_str
                    
                    events.append({
                        "message_id": message_id.decode() if isinstance(message_id, bytes) else message_id,
                        "fields": decoded_fields
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to read login events: {e}")
            return []
    
    def ack_login_event(self, consumer_group: str, message_id: str):
        """Acknowledge processed login event"""
        try:
            self._client.xack("logins:stream", consumer_group, message_id)
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
    
    # ===== REDIS TIMESERIES OPERATIONS =====
    
    def add_anomaly_score(self, user_id: str, score: float, timestamp: int = None) -> bool:
        """Add anomaly score to user's TimeSeries"""
        if not self._modules_available['timeseries']:
            logger.warning("TimeSeries not available, using fallback")
            return self._add_anomaly_score_fallback(user_id, score, timestamp)
        
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        
        try:
            ts_key = f"timeseries:{user_id}:anomaly"
            
            # Create time series if it doesn't exist
            try:
                self._client.execute_command(
                    "TS.CREATE", ts_key,
                    "RETENTION", 86400000,  # 24 hours
                    "LABELS", "user", user_id, "metric", "anomaly_score"
                )
            except Exception as e:
                if "TSDB: key already exists" not in str(e):
                    logger.warning(f"Could not create TimeSeries: {e}")
            
            # Add data point (timestamp in milliseconds)
            self._client.execute_command("TS.ADD", ts_key, timestamp * 1000, score)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add anomaly score: {e}")
            return False
    
    def get_anomaly_scores(self, user_id: str, hours: int = 24) -> List[tuple]:
        """Get user's anomaly scores from TimeSeries"""
        if not self._modules_available['timeseries']:
            return self._get_anomaly_scores_fallback(user_id, hours)
        
        try:
            ts_key = f"timeseries:{user_id}:anomaly"
            
            # Calculate time range in milliseconds
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (hours * 3600 * 1000)
            
            # Get time series data
            result = self._client.execute_command("TS.RANGE", ts_key, start_time, end_time)
            
            # Convert to list of (timestamp, score) tuples
            scores = []
            for timestamp_ms, score_bytes in result:
                timestamp = int(timestamp_ms) // 1000  # Convert back to seconds
                score = float(score_bytes)
                scores.append((timestamp, score))
            
            return scores
            
        except Exception as e:
            logger.error(f"Failed to get anomaly scores: {e}")
            return []
    
    # ===== REDIS JSON OPERATIONS =====
    
    def store_alert_json(self, alert_id: str, alert_data: Dict) -> bool:
        """Store security alert as JSON document"""
        if not self._modules_available['json']:
            return self._store_alert_fallback(alert_id, alert_data)
        
        try:
            key = f"alert:{alert_id}"
            self._client.execute_command("JSON.SET", key, "$", json.dumps(alert_data))
            return True
            
        except Exception as e:
            logger.error(f"Failed to store alert JSON: {e}")
            return False
    
    def get_alert_json(self, alert_id: str) -> Optional[Dict]:
        """Get security alert JSON document"""
        if not self._modules_available['json']:
            return self._get_alert_fallback(alert_id)
        
        try:
            key = f"alert:{alert_id}"
            result = self._client.execute_command("JSON.GET", key)
            
            if result:
                json_str = result.decode() if isinstance(result, bytes) else result
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get alert JSON: {e}")
            return None
    
    # ===== REDIS SEARCH OPERATIONS =====
    
    def search_alerts(self, query: str, limit: int = 100) -> List[Dict]:
        """Search alerts using RediSearch"""
        if not self._modules_available['search']:
            return self._search_alerts_fallback(query, limit)
        
        try:
            result = self._client.execute_command(
                "FT.SEARCH", "alerts_idx", query,
                "LIMIT", "0", str(limit)
            )
            
            alerts = []
            # Parse search results (skip count at index 0)
            for i in range(1, len(result), 2):
                doc_id = result[i].decode() if isinstance(result[i], bytes) else result[i]
                
                # Get the JSON document
                alert_data = self.get_alert_json(doc_id.replace("alert:", ""))
                if alert_data:
                    alerts.append(alert_data)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to search alerts: {e}")
            return []
    
    # ===== REDIS BLOOM FILTER OPERATIONS =====
    
    def check_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in malicious IP bloom filter"""
        if not self._modules_available['bloom']:
            return self._check_malicious_ip_fallback(ip)
        
        try:
            result = self._client.execute_command("BF.EXISTS", "bad_ips:bloom", ip)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to check malicious IP: {e}")
            return False
    
    def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP bloom filter"""
        if not self._modules_available['bloom']:
            return self._add_malicious_ip_fallback(ip)
        
        try:
            result = self._client.execute_command("BF.ADD", "bad_ips:bloom", ip)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to add malicious IP: {e}")
            return False
    
    # ===== VECTOR SEARCH OPERATIONS =====
    
    def store_embedding(self, user_id: str, timestamp: int, embedding: List[float]) -> bool:
        """Store behavior embedding for vector search"""
        if not self._modules_available['search']:
            return self._store_embedding_fallback(user_id, timestamp, embedding)
        
        try:
            key = f"embeddings:{user_id}:{timestamp}"
            
            # Convert embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            # Store in hash for vector search
            self._client.hset(key, mapping={
                "user_id": user_id,
                "timestamp": str(timestamp),
                "embedding": embedding_bytes
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False
    
    def vector_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Perform vector similarity search"""
        if not self._modules_available['search']:
            return self._vector_search_fallback(query_embedding, limit)
        
        try:
            # Convert query embedding to bytes
            query_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
            
            # Perform KNN search
            result = self._client.execute_command(
                "FT.SEARCH", "embeddings_idx",
                f"*=>[KNN {limit} @embedding $query_vector AS distance]",
                "PARAMS", "2", "query_vector", query_bytes,
                "SORTBY", "distance",
                "DIALECT", "2"
            )
            
            similar_embeddings = []
            # Parse results
            for i in range(1, len(result), 2):
                doc_id = result[i].decode() if isinstance(result[i], bytes) else result[i]
                doc_data = result[i + 1]
                
                # Parse document data
                embedding_data = {}
                for j in range(0, len(doc_data), 2):
                    field = doc_data[j].decode() if isinstance(doc_data[j], bytes) else doc_data[j]
                    value = doc_data[j + 1]
                    
                    if field == "distance":
                        embedding_data[field] = float(value)
                    elif field in ["user_id", "timestamp"]:
                        embedding_data[field] = value.decode() if isinstance(value, bytes) else value
                
                similar_embeddings.append(embedding_data)
            
            return similar_embeddings
            
        except Exception as e:
            logger.error(f"Failed to perform vector search: {e}")
            return []
    
    # ===== FALLBACK METHODS (for when modules are not available) =====
    
    def _add_anomaly_score_fallback(self, user_id: str, score: float, timestamp: int) -> bool:
        """Fallback method using sorted sets"""
        try:
            key = f"timeseries:{user_id}:anomaly"
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            self._client.zadd(key, {str(score): timestamp})
            
            # Keep only recent data
            cutoff = timestamp - (24 * 3600)
            self._client.zremrangebyscore(key, 0, cutoff)
            
            return True
        except Exception as e:
            logger.error(f"Fallback anomaly score storage failed: {e}")
            return False
    
    def _get_anomaly_scores_fallback(self, user_id: str, hours: int) -> List[tuple]:
        """Fallback method using sorted sets"""
        try:
            key = f"timeseries:{user_id}:anomaly"
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            result = self._client.zrangebyscore(key, start_time, end_time, withscores=True)
            return [(int(score), float(value)) for value, score in result]
        except Exception as e:
            logger.error(f"Fallback anomaly score retrieval failed: {e}")
            return []
    
    def _store_alert_fallback(self, alert_id: str, alert_data: Dict) -> bool:
        """Fallback using regular Redis string"""
        try:
            key = f"alert:{alert_id}"
            self._client.set(key, json.dumps(alert_data))
            return True
        except Exception as e:
            logger.error(f"Fallback alert storage failed: {e}")
            return False
    
    def _get_alert_fallback(self, alert_id: str) -> Optional[Dict]:
        """Fallback using regular Redis string"""
        try:
            key = f"alert:{alert_id}"
            result = self._client.get(key)
            if result:
                json_str = result.decode() if isinstance(result, bytes) else result
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Fallback alert retrieval failed: {e}")
            return None
    
    def _search_alerts_fallback(self, query: str, limit: int) -> List[Dict]:
        """Fallback using key pattern matching"""
        try:
            keys = self._client.keys("alert:*")
            alerts = []
            
            for key in keys[:limit]:
                key_str = key.decode() if isinstance(key, bytes) else key
                alert_id = key_str.replace("alert:", "")
                alert_data = self._get_alert_fallback(alert_id)
                if alert_data:
                    alerts.append(alert_data)
            
            return alerts
        except Exception as e:
            logger.error(f"Fallback alert search failed: {e}")
            return []
    
    def _check_malicious_ip_fallback(self, ip: str) -> bool:
        """Fallback using Redis set"""
        try:
            return bool(self._client.sismember("bad_ips:set", ip))
        except Exception as e:
            logger.error(f"Fallback IP check failed: {e}")
            return False
    
    def _add_malicious_ip_fallback(self, ip: str) -> bool:
        """Fallback using Redis set"""
        try:
            return bool(self._client.sadd("bad_ips:set", ip))
        except Exception as e:
            logger.error(f"Fallback IP addition failed: {e}")
            return False
    
    def _store_embedding_fallback(self, user_id: str, timestamp: int, embedding: List[float]) -> bool:
        """Fallback using hash"""
        try:
            key = f"embeddings:{user_id}:{timestamp}"
            self._client.hset(key, mapping={
                "user_id": user_id,
                "timestamp": str(timestamp),
                "embedding": json.dumps(embedding)
            })
            return True
        except Exception as e:
            logger.error(f"Fallback embedding storage failed: {e}")
            return False
    
    def _vector_search_fallback(self, query_embedding: List[float], limit: int) -> List[Dict]:
        """Fallback using cosine similarity"""
        try:
            keys = self._client.keys("embeddings:*")
            similarities = []
            
            for key in keys[:100]:  # Limit for performance
                try:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    data = self._client.hgetall(key_str)
                    
                    if b'embedding' in data:
                        stored_embedding = json.loads(data[b'embedding'].decode())
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)
                        
                        similarities.append({
                            'user_id': data[b'user_id'].decode(),
                            'timestamp': data[b'timestamp'].decode(),
                            'distance': 1 - similarity
                        })
                except:
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['distance'])
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Fallback vector search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        try:
            import math
            
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            if not vec1 or not vec2:
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception:
            return 0.0


# Global Redis Stack client instance
redis_stack_client = RedisStackClient()
