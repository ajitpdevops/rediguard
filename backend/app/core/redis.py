"""Redis connection and client management"""

import redis
from typing import Optional
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with basic Redis features"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._is_connected = False
    
    def connect(self) -> redis.Redis:
        """Connect to Redis"""
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                health_check_interval=30
            )
            
            # Test connection
            self._client.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            
            # Initialize basic Redis features
            self._initialize_redis_features()
            
            return self._client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _initialize_redis_features(self):
        """Initialize basic Redis features"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Initialize simple structures for our MVP
            self._initialize_basic_structures()
            
            logger.info("Redis basic features initialized successfully")
            
        except Exception as e:
            logger.warning(f"Error initializing Redis features: {e}")
    
    def _initialize_basic_structures(self):
        """Initialize basic Redis data structures for MVP"""
        try:
            # Initialize bloom filter simulation with a Set
            # In a real Redis Stack deployment, you'd use BF.RESERVE
            bloom_key = "bad_ips:set"  # Using a set instead of bloom filter for MVP
            
            # Add some sample malicious IPs for demo
            sample_malicious_ips = [
                "192.168.1.100",
                "10.0.0.50",
                "203.0.113.1",
                "198.51.100.1"
            ]
            
            for ip in sample_malicious_ips:
                self._client.sadd(bloom_key, ip)
            
            logger.info("Initialized basic Redis structures")
            
        except Exception as e:
            logger.error(f"Failed to initialize basic structures: {e}")
    
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
            logger.info("Redis connection closed")
    
    # Helper methods for Redis Stack feature simulation
    
    def check_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in malicious IP set (bloom filter simulation)"""
        try:
            return self._client.sismember("bad_ips:set", ip)
        except Exception as e:
            logger.error(f"Failed to check malicious IP: {e}")
            return False
    
    def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP set"""
        try:
            result = self._client.sadd("bad_ips:set", ip)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to add malicious IP: {e}")
            return False
    
    def store_timeseries_data(self, key: str, timestamp: int, value: float):
        """Store time series data using sorted sets"""
        try:
            # Use sorted set with timestamp as score
            self._client.zadd(key, {str(value): timestamp})
            
            # Keep only recent data (last 24 hours)
            import time
            cutoff = int(time.time()) - (24 * 3600)
            self._client.zremrangebyscore(key, 0, cutoff)
            
        except Exception as e:
            logger.error(f"Failed to store timeseries data: {e}")
    
    def get_timeseries_range(self, key: str, start_time: int, end_time: int) -> list:
        """Get time series data from sorted set"""
        try:
            # Get data in time range
            result = self._client.zrangebyscore(
                key, start_time, end_time, 
                withscores=True
            )
            return [(float(value), int(score)) for value, score in result]
        except Exception as e:
            logger.error(f"Failed to get timeseries range: {e}")
            return []
    
    def store_json_document(self, key: str, data: dict):
        """Store JSON document as string"""
        try:
            self._client.set(key, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to store JSON document: {e}")
    
    def get_json_document(self, key: str) -> dict:
        """Get JSON document"""
        try:
            data = self._client.get(key)
            if data:
                return json.loads(data)
            return {}
        except Exception as e:
            logger.error(f"Failed to get JSON document: {e}")
            return {}
    
    def search_keys_pattern(self, pattern: str) -> list:
        """Search keys by pattern"""
        try:
            return self._client.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to search keys: {e}")
            return []
    
    def store_vector_embedding(self, key: str, user_id: str, timestamp: int, embedding: list):
        """Store vector embedding as hash"""
        try:
            embedding_str = json.dumps(embedding)
            self._client.hset(key, mapping={
                "user_id": user_id,
                "timestamp": str(timestamp),
                "embedding": embedding_str
            })
        except Exception as e:
            logger.error(f"Failed to store vector embedding: {e}")
    
    def find_similar_embeddings(self, query_embedding: list, limit: int = 5) -> list:
        """Find similar embeddings (simplified cosine similarity)"""
        try:
            # For MVP, we'll do a simple similarity search
            # In production with Redis Stack, you'd use vector search
            embedding_keys = self.search_keys_pattern("embeddings:*")
            
            similarities = []
            for key in embedding_keys[:100]:  # Limit search for performance
                try:
                    data = self._client.hgetall(key)
                    if data and 'embedding' in data:
                        stored_embedding = json.loads(data['embedding'])
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)
                        similarities.append({
                            'user_id': data.get('user_id', ''),
                            'timestamp': int(data.get('timestamp', 0)),
                            'similarity': similarity,
                            'distance': 1 - similarity
                        })
                except:
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {e}")
            return []
    
    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            # Ensure same length
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            if not vec1 or not vec2:
                return 0.0
            
            # Calculate dot product and magnitudes
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0


# Global Redis client instance
redis_client = RedisClient()
