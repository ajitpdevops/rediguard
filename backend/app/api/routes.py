"""Main API router and endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from app.models import (
    LoginEvent, SecurityAlert, AlertQuery, AlertResponse, 
    AnomalyScore, HealthCheck
)
from app.services.security_service import SecurityService
from app.services.ai_service import ai_service
from app.core.redis_stack import redis_stack_client

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Service instances
security_service = SecurityService()
# ai_service is imported directly as a global instance


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_connected = False
        features_initialized = False
        
        try:
            client = redis_stack_client.client
            client.ping()
            redis_connected = True
            
            # Check if basic features are initialized
            try:
                # Check if basic structures exist
                client.exists("bad_ips:set")
                features_initialized = True
            except:
                pass
                
        except:
            pass
        
        status = "healthy" if redis_connected else "unhealthy"
        
        return HealthCheck(
            status=status,
            redis_connected=redis_connected,
            features_initialized=features_initialized
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/events/login")
async def ingest_login_event(event: LoginEvent):
    """Ingest a new login event"""
    try:
        result = await security_service.process_login_event(event)
        return {
            "message": "Login event processed successfully",
            "user_id": event.user_id,
            "anomaly_score": result.get("anomaly_score"),
            "is_anomaly": result.get("is_anomaly"),
            "features": result.get("features"),
            "embedding": result.get("embedding"),
            "similar_events": result.get("similar_events"),
            "alert": result.get("alert")
        }
        
    except Exception as e:
        logger.error(f"Failed to ingest login event: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest login event")


@router.get("/alerts/search", response_model=AlertResponse)
async def search_alerts(
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    user_id: Optional[str] = None,
    ip: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
):
    """Search security alerts"""
    try:
        query_params = {
            "min_score": min_score,
            "max_score": max_score,
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "ip": ip,
            "location": location,
            "limit": limit
        }
        
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}
        
        alerts = await security_service.get_security_alerts("*", limit)
        
        return AlertResponse(
            alerts=alerts,
            total=len(alerts),
            query_params=AlertQuery(**query_params)
        )
        
    except Exception as e:
        logger.error(f"Failed to search alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to search alerts")


@router.get("/users/{user_id}/anomaly-history", response_model=List[AnomalyScore])
async def get_user_anomaly_history(user_id: str, hours: int = 24):
    """Get anomaly score history for a user"""
    try:
        history = await security_service.get_user_anomaly_history(user_id, hours)
        return history
        
    except Exception as e:
        logger.error(f"Failed to get anomaly history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get anomaly history")


@router.get("/ip/{ip}/reputation")
async def get_ip_reputation(ip: str):
    """Get IP reputation check"""
    try:
        result = await security_service.check_ip_reputation(ip)
        return result
        
    except Exception as e:
        logger.error(f"Failed to check IP reputation: {e}")
        raise HTTPException(status_code=500, detail="Failed to check IP reputation")


@router.get("/users/{user_id}/similar-behavior")
async def get_similar_behavior(user_id: str, limit: int = 5):
    """Get similar behavior patterns for a user"""
    try:
        similar_events = await security_service.find_similar_behavior(user_id, limit=limit)
        return {"similar_events": similar_events}
        
    except Exception as e:
        logger.error(f"Failed to find similar behavior: {e}")
        raise HTTPException(status_code=500, detail="Failed to find similar behavior")


@router.post("/security/add-malicious-ip")
async def add_malicious_ip(ip: str):
    """Add an IP to the malicious IP blocklist"""
    try:
        result = await security_service.add_malicious_ip(ip)
        return {
            "message": f"IP {ip} added to malicious IP filter",
            "success": result
        }
        
    except Exception as e:
        logger.error(f"Failed to add malicious IP: {e}")
        raise HTTPException(status_code=500, detail="Failed to add malicious IP")


@router.get("/security/check-ip/{ip}")
async def check_malicious_ip(ip: str):
    """Check if an IP is in the malicious IP blocklist"""
    try:
        result = await security_service.check_ip_reputation(ip)
        return {
            "ip": ip,
            "is_malicious": result.get("is_malicious", False),
            "checked_at": result.get("checked_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to check malicious IP: {e}")
        raise HTTPException(status_code=500, detail="Failed to check malicious IP")


@router.post("/ai/analyze-event")
async def analyze_event(event: LoginEvent):
    """Analyze a login event and return anomaly score and features"""
    try:
        # Extract features
        features = ai_service.extract_features(event)
        
        # Calculate anomaly score
        anomaly_score = ai_service.predict_anomaly_score(features)
        
        # Generate behavior embedding
        embedding = ai_service.generate_behavior_embedding(event, features)
        
        # Find similar behaviors
        similar_behaviors = await security_service.find_similar_behavior(event.user_id, event.timestamp, limit=5)
        
        return {
            "user_id": event.user_id,
            "anomaly_score": anomaly_score,
            "features": features,
            "embedding_dimension": len(embedding),
            "similar_behaviors": similar_behaviors
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze event: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze event")


@router.get("/stats/overview")
async def get_overview_stats():
    """Get overview statistics"""
    try:
        client = redis_stack_client.client
        
        # Get stream length
        stream_length = client.xlen("logins:stream")
        
        # Get total alerts (search for alert documents)
        try:
            alert_search_result = redis_stack_client.search_alerts("*", limit=1000)
            total_alerts = len(alert_search_result)
        except:
            total_alerts = 0
        
        # Get malicious IP count
        malicious_ip_count = client.scard("bad_ips:set")
        
        return {
            "stream_length": stream_length,
            "total_alerts": total_alerts,
            "malicious_ip_count": malicious_ip_count,
            "redis_connected": True
        }
        
    except Exception as e:
        logger.error(f"Failed to get overview stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get overview stats")


@router.post("/demo/generate-data")
async def generate_demo_data(num_events: int = 10):
    """Generate demo data for testing Redis 8 features"""
    try:
        events = await security_service.generate_test_data(num_events)
        return {
            "message": f"Generated {num_events} demo events",
            "events": events
        }
        
    except Exception as e:
        logger.error(f"Failed to generate demo data: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate demo data")


@router.post("/demo/generate-events")
async def generate_demo_events(count: int = 10):
    """Generate demo login events for testing"""
    try:
        import random
        import time
        from datetime import datetime, timedelta
        
        users = ["alice", "bob", "charlie", "diana", "eve"]
        locations = [
            "New York, US", "London, UK", "Tokyo, JP", "Sydney, AU", 
            "Berlin, DE", "Toronto, CA", "Mumbai, IN", "São Paulo, BR"
        ]
        
        events_created = []
        current_time = int(datetime.now().timestamp())
        
        for i in range(count):
            # Create some normal and some anomalous events
            is_anomalous = random.random() < 0.2  # 20% anomalous
            
            if is_anomalous:
                # Anomalous event: unusual location, time, or IP
                user_id = random.choice(users)
                ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                location = random.choice(locations)
                # Random time in the past week
                timestamp = current_time - random.randint(0, 7 * 24 * 3600)
            else:
                # Normal event
                user_id = random.choice(users)
                ip = f"192.168.{random.randint(1, 10)}.{random.randint(1, 100)}"
                location = random.choice(locations[:3])  # Common locations
                # Recent timestamp
                timestamp = current_time - random.randint(0, 24 * 3600)
            
            event = LoginEvent(
                user_id=user_id,
                ip=ip,
                location=location,
                timestamp=timestamp
            )
            
            result = await security_service.process_login_event(event)
            events_created.append({
                "event": event.dict(),
                "result": result,
                "is_anomalous": is_anomalous
            })
        
        return {
            "message": f"Generated {count} demo events",
            "events": events_created
        }
        
    except Exception as e:
        logger.error(f"Failed to generate demo events: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate demo events")
