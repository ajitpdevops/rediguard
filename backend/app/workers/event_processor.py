"""Security event processor worker"""

import asyncio
import json
import logging
from typing import Dict, Any

from app.core.redis import redis_client
from app.core.config import settings
from app.services.security_service import SecurityService
from app.services.ai_service import AIService
from app.models import LoginEvent, SecurityAlert, BehaviorEmbedding

logger = logging.getLogger(__name__)


class SecurityEventProcessor:
    """Worker for processing security events from Redis Streams"""
    
    def __init__(self):
        self.security_service = SecurityService()
        self.ai_service = AIService()
        self.redis = redis_client
        self.running = False
    
    async def start(self):
        """Start the event processor"""
        self.running = True
        logger.info("Starting security event processor")
        
        # Create consumer group if it doesn't exist
        await self._create_consumer_group()
        
        # Start processing loop
        while self.running:
            try:
                await self._process_events()
                await asyncio.sleep(1)  # Short delay between polls
                
            except Exception as e:
                logger.error(f"Error in event processor: {e}")
                await asyncio.sleep(5)  # Longer delay on error
    
    async def stop(self):
        """Stop the event processor"""
        self.running = False
        logger.info("Stopping security event processor")
    
    async def _create_consumer_group(self):
        """Create Redis Stream consumer group"""
        try:
            client = self.redis.client
            client.xgroup_create(
                "logins:stream",
                settings.stream_consumer_group,
                id="0",
                mkstream=True
            )
            logger.info(f"Created consumer group: {settings.stream_consumer_group}")
            
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.info("Consumer group already exists")
            else:
                logger.error(f"Failed to create consumer group: {e}")
                raise
    
    async def _process_events(self):
        """Process events from the stream"""
        try:
            client = self.redis.client
            
            # Read from stream
            messages = client.xreadgroup(
                settings.stream_consumer_group,
                settings.stream_consumer_name,
                {"logins:stream": ">"},
                count=10,
                block=1000  # Block for 1 second
            )
            
            for stream_name, stream_messages in messages:
                for message_id, fields in stream_messages:
                    await self._process_single_event(message_id, fields)
                    
                    # Acknowledge the message
                    client.xack("logins:stream", settings.stream_consumer_group, message_id)
                    
        except Exception as e:
            if "NOGROUP" not in str(e):  # Ignore missing group errors
                logger.error(f"Failed to process events: {e}")
    
    async def _process_single_event(self, message_id: str, fields: Dict[str, str]):
        """Process a single login event"""
        try:
            # Parse the event
            event = LoginEvent(
                user_id=fields["user_id"],
                ip=fields["ip"],
                location=fields["location"],
                timestamp=int(fields["timestamp"])
            )
            
            logger.info(f"Processing event {message_id} for user {event.user_id}")
            
            # Extract features for AI analysis
            features = self.ai_service.extract_features(event)
            
            # Calculate anomaly score
            anomaly_score = self.ai_service.predict_anomaly_score(features)
            
            # Store anomaly score in time series
            await self.security_service.store_anomaly_score(
                event.user_id,
                event.timestamp,
                anomaly_score
            )
            
            # Generate behavior embedding
            embedding = self.ai_service.generate_behavior_embedding(event, features)
            behavior_embedding = BehaviorEmbedding(
                user_id=event.user_id,
                timestamp=event.timestamp,
                embedding=embedding
            )
            
            # Store behavior embedding
            await self.security_service.store_behavior_embedding(behavior_embedding)
            
            # Check for malicious IP
            is_malicious_ip = await self.security_service.check_malicious_ip(event.ip)
            
            # Calculate geographic jump
            geo_distance = await self.security_service.calculate_geo_distance(
                event.location,
                event.user_id
            )
            
            # Determine if this should trigger an alert
            should_alert = (
                anomaly_score >= settings.anomaly_threshold or
                is_malicious_ip or
                geo_distance >= settings.geo_jump_threshold
            )
            
            if should_alert:
                # Create and store security alert
                alert = SecurityAlert(
                    user_id=event.user_id,
                    ip=event.ip,
                    score=anomaly_score,
                    location=event.location,
                    geo_jump_km=geo_distance,
                    embedding=embedding,
                    timestamp=event.timestamp,
                    is_malicious_ip=is_malicious_ip
                )
                
                await self.security_service.store_security_alert(alert)
                
                logger.warning(
                    f"SECURITY ALERT: User {event.user_id}, Score: {anomaly_score:.3f}, "
                    f"Malicious IP: {is_malicious_ip}, Geo Jump: {geo_distance:.1f}km"
                )
            
        except Exception as e:
            logger.error(f"Failed to process event {message_id}: {e}")


# Global processor instance
event_processor = SecurityEventProcessor()
