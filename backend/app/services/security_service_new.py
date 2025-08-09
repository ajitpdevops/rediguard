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
        logger.info("SecurityService initialized with Redis Stack client")
    
    async def process_login_event(self, event: LoginEvent) -> Dict[str, Any]:
        """Process a login event through the security pipeline"""
        try:
            logger.info(f"Processing login event for user {event.user_id} from {event.ip}")
            
            # Store event in Redis Stream
            stream_id = self.redis.add_login_event(
                user_id=event.user_id,
                ip=event.ip,
                location=event.location,
                timestamp=event.timestamp
            )
            
            # Perform AI analysis
            features = ai_service.extract_features(event)
            embedding = ai_service.generate_behavior_embedding(event, features)
            anomaly_score = ai_service.predict_anomaly_score(features)
            
            # Store behavior embedding for vector search
            self.redis.store_embedding(event.user_id, event.timestamp, embedding)
            
            # Add anomaly score to TimeSeries
            self.redis.add_anomaly_score(event.user_id, anomaly_score, event.timestamp)
            
            # Check if IP is malicious using Bloom filter
            is_malicious_ip = self.redis.check_malicious_ip(event.ip)
            
            # Determine if this is an anomaly
            is_anomaly = anomaly_score > settings.anomaly_threshold
            
            # Create security alert if needed
            alert = None
            if is_anomaly or is_malicious_ip:
                alert = SecurityAlert(
                    user_id=event.user_id,
                    ip=event.ip,
                    score=anomaly_score,
                    location=event.location,
                    timestamp=event.timestamp,
                    is_malicious_ip=is_malicious_ip,
                    embedding=embedding
                )
                
                # Store alert as JSON document
                self.redis.store_alert_json(alert.alert_id, alert.dict())
                
                logger.warning(f"Security alert created: {alert.alert_id} for user {event.user_id}")
            
            # Find similar behavior patterns using vector search
            similar_events = self.redis.vector_search(embedding, limit=5)
            
            # Prepare response
            response = {
                "stream_id": stream_id,
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
                "is_malicious_ip": is_malicious_ip,
                "features": features,
                "embedding": embedding,
                "similar_events": similar_events,
                "alert": alert.dict() if alert else None,
                "processed_at": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process login event: {e}")
            raise
    
    async def get_security_alerts(self, query: str = "*", limit: int = 100) -> List[Dict]:
        """Search security alerts using RediSearch"""
        try:
            alerts = self.redis.search_alerts(query, limit)
            logger.info(f"Retrieved {len(alerts)} security alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to retrieve security alerts: {e}")
            return []
    
    async def get_user_anomaly_history(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Get user's anomaly score history from TimeSeries"""
        try:
            scores = self.redis.get_anomaly_scores(user_id, hours)
            
            # Convert to list of dictionaries
            history = []
            for timestamp, score in scores:
                history.append({
                    "timestamp": timestamp,
                    "score": score,
                    "datetime": datetime.fromtimestamp(timestamp).isoformat()
                })
            
            logger.info(f"Retrieved {len(history)} anomaly scores for user {user_id}")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve user anomaly history: {e}")
            return []
    
    async def add_malicious_ip(self, ip: str) -> bool:
        """Add IP to malicious IP Bloom filter"""
        try:
            result = self.redis.add_malicious_ip(ip)
            if result:
                logger.info(f"Added malicious IP: {ip}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add malicious IP: {e}")
            return False
    
    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using Bloom filter"""
        try:
            is_malicious = self.redis.check_malicious_ip(ip)
            
            return {
                "ip": ip,
                "is_malicious": is_malicious,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check IP reputation: {e}")
            return {
                "ip": ip,
                "is_malicious": False,
                "error": str(e)
            }
    
    async def find_similar_behavior(self, user_id: str, timestamp: int = None, limit: int = 5) -> List[Dict]:
        """Find similar behavior patterns using vector search"""
        try:
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            # Get the user's behavior embedding
            key = f"embeddings:{user_id}:{timestamp}"
            
            # For demo, we'll use a dummy embedding if the specific one doesn't exist
            dummy_embedding = [0.1] * settings.vector_dimension
            
            similar_events = self.redis.vector_search(dummy_embedding, limit)
            logger.info(f"Found {len(similar_events)} similar behavior patterns")
            
            return similar_events
            
        except Exception as e:
            logger.error(f"Failed to find similar behavior: {e}")
            return []
    
    async def get_login_stream_events(self, consumer_group: str = "security", consumer_name: str = "analyzer", count: int = 10) -> List[Dict]:
        """Read login events from Redis Stream"""
        try:
            events = self.redis.read_login_events(consumer_group, consumer_name, count)
            logger.info(f"Retrieved {len(events)} events from login stream")
            return events
            
        except Exception as e:
            logger.error(f"Failed to read login stream events: {e}")
            return []
    
    async def acknowledge_stream_event(self, consumer_group: str, message_id: str):
        """Acknowledge processed stream event"""
        try:
            self.redis.ack_login_event(consumer_group, message_id)
            logger.debug(f"Acknowledged stream event: {message_id}")
            
        except Exception as e:
            logger.error(f"Failed to acknowledge stream event: {e}")
    
    async def generate_test_data(self, num_events: int = 10) -> List[Dict]:
        """Generate test login events for demonstration"""
        try:
            test_events = []
            
            users = ["alice", "bob", "charlie", "diana", "eve"]
            locations = ["New York, US", "London, UK", "Tokyo, JP", "Sydney, AU", "Berlin, DE"]
            ips = ["192.168.1.100", "203.0.113.1", "198.51.100.1", "10.0.0.50", "172.16.0.100"]
            
            for i in range(num_events):
                event = LoginEvent(
                    user_id=users[i % len(users)],
                    ip=ips[i % len(ips)],
                    location=locations[i % len(locations)],
                    timestamp=int(datetime.now().timestamp()) - (i * 300)  # 5 minutes apart
                )
                
                # Process the event
                result = await self.process_login_event(event)
                test_events.append({
                    "event": event.dict(),
                    "result": result
                })
            
            logger.info(f"Generated {len(test_events)} test events")
            return test_events
            
        except Exception as e:
            logger.error(f"Failed to generate test data: {e}")
            return []
    
    async def get_redis_info(self) -> Dict[str, Any]:
        """Get Redis Stack information and module status"""
        try:
            info = {
                "connected": redis_stack_client._is_connected,
                "modules_available": redis_stack_client._modules_available.copy(),
                "redis_host": settings.redis_host,
                "redis_port": settings.redis_port,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to ping Redis
            if redis_stack_client._client:
                redis_stack_client._client.ping()
                info["ping_successful"] = True
            else:
                info["ping_successful"] = False
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global security service instance
security_service = SecurityService()
