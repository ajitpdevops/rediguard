"""Security service with Redis Stack 8 features"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

from app.core.redis_stack import redis_stack_client
from app.core.config import settings
from app.models import LoginEvent, SecurityAlert, AnomalyResult, AnomalyScore, BehaviorEmbedding
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class SecurityService:
    """Security service using Redis Stack 8 features"""
    
    def __init__(self):
        self.redis = redis_stack_client
        self.ai_service = ai_service
    
    async def process_login_event(self, event: LoginEvent) -> SecurityAlert:
        """Process login event using Redis Stack features"""
        try:
            # Add to Redis Stream for real-time processing
            timestamp = int(event.timestamp.timestamp()) if event.timestamp else int(datetime.now().timestamp())
            
            stream_id = self.redis.add_login_event(
                user_id=event.user_id,
                ip=event.ip,
                location=event.location or "Unknown",
                timestamp=timestamp
            )
            
            logger.info(f"Added login event to stream: {stream_id}")
            
            # Check if IP is malicious using Bloom Filter
            is_malicious_ip = self.redis.check_malicious_ip(event.ip)
            
            # Get AI analysis
            analysis = await self.ai_service.analyze_login_behavior(event)
            
            # Store anomaly score in TimeSeries
            if analysis.anomaly_score > 0:
                self.redis.add_anomaly_score(
                    user_id=event.user_id,
                    score=analysis.anomaly_score,
                    timestamp=timestamp
                )
            
            # Create security alert
            alert = SecurityAlert(
                id=str(uuid.uuid4()),
                user_id=event.user_id,
                event_type="login",
                ip=event.ip,
                location=event.location or "Unknown",
                timestamp=event.timestamp or datetime.now(),
                score=analysis.anomaly_score,
                is_malicious_ip=is_malicious_ip,
                geo_jump_km=getattr(analysis, 'geo_jump_km', 0),
                details=analysis.details
            )
            
            # Store alert as JSON document
            alert_data = {
                "id": alert.id,
                "user_id": alert.user_id,
                "event_type": alert.event_type,
                "ip": alert.ip,
                "location": alert.location,
                "timestamp": alert.timestamp.isoformat(),
                "score": alert.score,
                "is_malicious_ip": alert.is_malicious_ip,
                "geo_jump_km": alert.geo_jump_km,
                "details": alert.details
            }
            
            self.redis.store_alert_json(alert.id, alert_data)
            
            # Store behavior embedding for vector search
            if hasattr(analysis, 'embedding') and analysis.embedding:
                self.redis.store_embedding(
                    user_id=event.user_id,
                    timestamp=timestamp,
                    embedding=analysis.embedding
                )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error processing login event: {e}")
            raise
    
    async def get_user_anomaly_history(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Get user's anomaly score history from TimeSeries"""
        try:
            scores = self.redis.get_anomaly_scores(user_id, hours)
            
            history = []
            for timestamp, score in scores:
                history.append({
                    "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                    "score": score,
                    "user_id": user_id
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting anomaly history: {e}")
            return []
    
    async def search_alerts(self, query: str = "*", limit: int = 100) -> List[Dict]:
        """Search alerts using RediSearch"""
        try:
            # If no specific query, get all alerts
            search_query = query if query != "*" else "*"
            
            alerts = self.redis.search_alerts(search_query, limit)
            return alerts
            
        except Exception as e:
            logger.error(f"Error searching alerts: {e}")
            return []
    
    async def get_alert_by_id(self, alert_id: str) -> Optional[SecurityAlert]:
        """Get specific alert by ID"""
        try:
            alert_data = self.redis.get_alert_json(alert_id)
            
            if alert_data:
                return SecurityAlert(
                    id=alert_data["id"],
                    user_id=alert_data["user_id"],
                    event_type=alert_data["event_type"],
                    ip=alert_data["ip"],
                    location=alert_data["location"],
                    timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                    score=alert_data["score"],
                    is_malicious_ip=alert_data["is_malicious_ip"],
                    geo_jump_km=alert_data.get("geo_jump_km", 0),
                    details=alert_data.get("details", {})
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting alert {alert_id}: {e}")
            return None
    
    async def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP Bloom Filter"""
        try:
            result = self.redis.add_malicious_ip(ip)
            logger.info(f"Added malicious IP {ip} to bloom filter")
            return result
            
        except Exception as e:
            logger.error(f"Error adding malicious IP: {e}")
            return False
    
    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using Bloom Filter"""
        try:
            is_malicious = self.redis.check_malicious_ip(ip)
            
            return {
                "ip": ip,
                "is_malicious": is_malicious,
                "source": "bloom_filter"
            }
            
        except Exception as e:
            logger.error(f"Error checking IP reputation: {e}")
            return {"ip": ip, "is_malicious": False, "source": "error"}
    
    async def find_similar_behaviors(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Find similar user behaviors using vector search"""
        try:
            # Get recent behavior embedding for this user
            scores = self.redis.get_anomaly_scores(user_id, hours=1)
            
            if not scores:
                return []
            
            # Use AI service to create query embedding
            dummy_event = LoginEvent(
                user_id=user_id,
                ip="0.0.0.0",
                location="Unknown",
                timestamp=datetime.now()
            )
            
            analysis = await self.ai_service.analyze_login_behavior(dummy_event)
            
            if hasattr(analysis, 'embedding') and analysis.embedding:
                similar = self.redis.vector_search(analysis.embedding, limit)
                return similar
            
            return []
            
        except Exception as e:
            logger.error(f"Error finding similar behaviors: {e}")
            return []
    
    async def get_real_time_events(self, consumer_group: str = "security_processor", 
                                 consumer_name: str = "worker_1", count: int = 10) -> List[Dict]:
        """Get real-time login events from Redis Stream"""
        try:
            events = self.redis.read_login_events(consumer_group, consumer_name, count)
            
            # Acknowledge processed events
            for event in events:
                self.redis.ack_login_event(consumer_group, event["message_id"])
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting real-time events: {e}")
            return []
    
    async def get_high_risk_alerts(self, threshold: float = 0.7, limit: int = 50) -> List[Dict]:
        """Get high-risk alerts using RediSearch"""
        try:
            # Search for alerts with high anomaly scores
            query = f"@score:[{threshold} +inf]"
            alerts = self.redis.search_alerts(query, limit)
            
            # Sort by score descending
            alerts.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting high-risk alerts: {e}")
            return []
    
    async def get_user_alerts(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get alerts for specific user"""
        try:
            query = f"@user_id:{user_id}"
            alerts = self.redis.search_alerts(query, limit)
            
            # Sort by timestamp descending
            alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats = {
                "redis_connected": self.redis._is_connected,
                "modules_available": self.redis._modules_available,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to get some basic stats
            try:
                if self.redis._client:
                    info = self.redis._client.info()
                    stats["redis_version"] = info.get("redis_version", "unknown")
                    stats["used_memory_human"] = info.get("used_memory_human", "unknown")
                    stats["connected_clients"] = info.get("connected_clients", 0)
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}


# Global security service instance
security_service = SecurityService()

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

from app.core.redis_stack import redis_stack_client
from app.models import LoginEvent, SecurityAlert, AnomalyResult
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class SecurityService:
    """Service for processing security events and detecting anomalies"""
    
    def __init__(self):
        self.redis = redis_client
    
    async def ingest_login_event(self, event: LoginEvent) -> str:
        """Ingest a login event into Redis Stream"""
        try:
            client = self.redis.client
            
            # Add event to Redis Stream
            stream_id = client.xadd(
                "logins:stream",
                {
                    "user_id": event.user_id,
                    "ip": event.ip,
                    "location": event.location,
                    "timestamp": str(event.timestamp)
                },
                maxlen=settings.redis_stream_maxlen
            )
            
            logger.info(f"Ingested login event for user {event.user_id}: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to ingest login event: {e}")
            raise
    
    async def check_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in the malicious IP bloom filter"""
        try:
            return self.redis.check_malicious_ip(ip)
            
        except Exception as e:
            logger.error(f"Failed to check malicious IP: {e}")
            return False
    
    async def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP bloom filter"""
        try:
            result = self.redis.add_malicious_ip(ip)
            logger.info(f"Added IP {ip} to malicious IP filter")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add malicious IP: {e}")
            return False
    
    async def store_anomaly_score(self, user_id: str, timestamp: int, score: float):
        """Store anomaly score in Redis TimeSeries"""
        try:
            key = f"timeseries:{user_id}:anomaly"
            self.redis.store_timeseries_data(key, timestamp, score)
            logger.debug(f"Stored anomaly score for user {user_id}: {score}")
            
        except Exception as e:
            logger.error(f"Failed to store anomaly score: {e}")
            raise
    
    async def get_user_anomaly_history(self, user_id: str, hours: int = 24) -> List[AnomalyScore]:
        """Get anomaly score history for a user"""
        try:
            key = f"timeseries:{user_id}:anomaly"
            
            # Calculate time range
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            # Get time series data
            result = self.redis.get_timeseries_range(key, start_time, end_time)
            
            history = []
            for score, timestamp in result:
                history.append(AnomalyScore(
                    user_id=user_id,
                    timestamp=timestamp,
                    score=score
                ))
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get anomaly history: {e}")
            return []
    
    async def store_behavior_embedding(self, embedding: BehaviorEmbedding):
        """Store behavior embedding in Redis for vector search"""
        try:
            key = f"embeddings:{embedding.user_id}:{embedding.timestamp}"
            self.redis.store_vector_embedding(
                key, 
                embedding.user_id, 
                embedding.timestamp, 
                embedding.embedding
            )
            logger.debug(f"Stored behavior embedding for user {embedding.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store behavior embedding: {e}")
            raise
    
    async def find_similar_behaviors(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar behavior patterns using vector search"""
        try:
            similar_behaviors = self.redis.find_similar_embeddings(query_embedding, limit)
            return similar_behaviors
            
        except Exception as e:
            logger.error(f"Failed to find similar behaviors: {e}")
            return []
    
    async def store_security_alert(self, alert: SecurityAlert):
        """Store security alert as JSON document"""
        try:
            key = f"alert:{alert.user_id}:{alert.timestamp}"
            alert_data = alert.model_dump()
            self.redis.store_json_document(key, alert_data)
            logger.info(f"Stored security alert for user {alert.user_id} with score {alert.score}")
            
        except Exception as e:
            logger.error(f"Failed to store security alert: {e}")
            raise
    
    async def search_alerts(self, query_params: Dict[str, Any]) -> List[SecurityAlert]:
        """Search alerts using simple pattern matching"""
        try:
            # Get all alert keys
            alert_keys = self.redis.search_keys_pattern("alert:*")
            
            alerts = []
            for key in alert_keys:
                try:
                    alert_data = self.redis.get_json_document(key)
                    if not alert_data:
                        continue
                    
                    # Apply filters
                    if self._alert_matches_query(alert_data, query_params):
                        alerts.append(SecurityAlert(**alert_data))
                        
                    # Limit results
                    if len(alerts) >= query_params.get("limit", 100):
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to parse alert {key}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            alerts.sort(key=lambda x: x.timestamp, reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to search alerts: {e}")
            return []
    
    def _alert_matches_query(self, alert_data: Dict[str, Any], query_params: Dict[str, Any]) -> bool:
        """Check if alert matches query parameters"""
        try:
            # Score range filter
            if query_params.get("min_score") is not None:
                if alert_data.get("score", 0) < query_params["min_score"]:
                    return False
            
            if query_params.get("max_score") is not None:
                if alert_data.get("score", 0) > query_params["max_score"]:
                    return False
            
            # Time range filter
            if query_params.get("start_time") is not None:
                if alert_data.get("timestamp", 0) < query_params["start_time"]:
                    return False
            
            if query_params.get("end_time") is not None:
                if alert_data.get("timestamp", 0) > query_params["end_time"]:
                    return False
            
            # Exact match filters
            if query_params.get("user_id"):
                if alert_data.get("user_id") != query_params["user_id"]:
                    return False
            
            if query_params.get("ip"):
                if alert_data.get("ip") != query_params["ip"]:
                    return False
            
            if query_params.get("location"):
                if query_params["location"].lower() not in alert_data.get("location", "").lower():
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to match alert query: {e}")
            return False
    
    async def calculate_geo_distance(self, current_location: str, user_id: str) -> float:
        """Calculate geographic distance from user's last known location"""
        try:
            client = self.redis.client
            
            # Get user's last location from a simple key
            last_location_key = f"user:{user_id}:last_location"
            last_location = client.get(last_location_key)
            
            if not last_location:
                # First time seeing this user, store current location
                client.set(last_location_key, current_location)
                return 0.0
            
            # Parse coordinates from location strings (simplified)
            # In a real implementation, you'd use a geocoding service
            distance = self._calculate_distance_between_locations(last_location, current_location)
            
            # Update last known location
            client.set(last_location_key, current_location)
            
            return distance
            
        except Exception as e:
            logger.error(f"Failed to calculate geo distance: {e}")
            return 0.0
    
    def _calculate_distance_between_locations(self, loc1: str, loc2: str) -> float:
        """Calculate distance between two location strings"""
        # Simplified implementation - in reality you'd geocode the location strings
        # For demo purposes, return a random distance if locations are different
        if loc1 != loc2:
            # Return a simulated distance based on location strings
            return abs(hash(loc1) - hash(loc2)) % 20000  # Random distance up to 20,000 km
        return 0.0
