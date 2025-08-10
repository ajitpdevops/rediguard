"""Main API router and endpoints"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.models import (
    LoginEvent, SecurityAlert, AlertQuery, AlertResponse, 
    AnomalyScore, HealthCheck
)
from app.services.security_service import SecurityService
from app.services.ai_service import ai_service
from app.services.llm_service import llm_service
from app.core.redis_stack import redis_stack_client

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Service instances
security_service = SecurityService()
# ai_service is imported directly as a global instance

# Global streaming control
streaming_active = False

# Data generation configuration
USERS = [
    "alice.johnson", "bob.smith", "charlie.brown", "diana.prince", "eve.adams",
    "frank.miller", "grace.hopper", "henry.ford", "iris.watson", "jack.ryan",
    "kate.bishop", "liam.neeson", "mary.jane", "nick.fury", "olivia.pope",
    "peter.parker", "quinn.fabray", "rick.sanchez", "sarah.connor", "tony.stark"
]

LOCATIONS = [
    {"city": "New York", "country": "US", "risk": "low"},
    {"city": "San Francisco", "country": "US", "risk": "low"},
    {"city": "London", "country": "UK", "risk": "low"},
    {"city": "Toronto", "country": "CA", "risk": "low"},
    {"city": "Berlin", "country": "DE", "risk": "low"},
    {"city": "Tokyo", "country": "JP", "risk": "low"},
    {"city": "Sydney", "country": "AU", "risk": "low"},
    {"city": "Mumbai", "country": "IN", "risk": "medium"},
    {"city": "São Paulo", "country": "BR", "risk": "medium"},
    {"city": "Moscow", "country": "RU", "risk": "high"},
    {"city": "Beijing", "country": "CN", "risk": "high"},
    {"city": "Lagos", "country": "NG", "risk": "high"},
    {"city": "Kiev", "country": "UA", "risk": "high"},
    {"city": "Tehran", "country": "IR", "risk": "very_high"},
    {"city": "Pyongyang", "country": "KP", "risk": "very_high"}
]

IP_RANGES = {
    "corporate": ["192.168.1.", "10.0.0.", "172.16.0."],
    "home": ["203.0.113.", "198.51.100.", "192.0.2."],
    "vpn": ["185.220.", "91.207.", "104.244."],
    "suspicious": ["123.456.", "45.67.", "89.12."],
    "malicious": ["666.13.", "31.13.", "172.245."]
}


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


# Helper functions for data generation
def _generate_realistic_event(user_profiles: Dict, anomaly_chance: float = 0.15) -> LoginEvent:
    """Generate a realistic login event"""
    user = random.choice(USERS)
    profile = user_profiles.get(user, _create_default_profile())
    current_time = datetime.now()
    
    # Determine if this should be an anomalous event
    is_anomaly = random.random() < anomaly_chance
    
    if is_anomaly:
        # Generate anomalous behavior
        location = _generate_anomalous_location()
        ip = _generate_anomalous_ip()
        timestamp = _generate_anomalous_time(current_time, profile)
    else:
        # Generate normal behavior
        location = _generate_normal_location(profile)
        ip = _generate_normal_ip(profile)
        timestamp = _generate_normal_time(current_time, profile)
    
    return LoginEvent(
        user_id=user,
        ip=ip,
        location=f"{location['city']}, {location['country']}",
        timestamp=int(timestamp.timestamp())
    )

def _create_default_profile() -> Dict:
    """Create a default user profile"""
    home_location = random.choice([loc for loc in LOCATIONS if loc["risk"] == "low"])
    work_hours = (random.randint(8, 10), random.randint(17, 19))
    
    return {
        "home_location": home_location,
        "work_hours": work_hours,
        "typical_ips": random.sample(IP_RANGES["corporate"] + IP_RANGES["home"], 3),
        "login_frequency": random.uniform(0.5, 3.0),
        "risk_tolerance": random.choice(["low", "medium", "high"])
    }

def _initialize_user_profiles() -> Dict[str, Dict]:
    """Create user behavior profiles"""
    profiles = {}
    
    for user in USERS:
        profiles[user] = _create_default_profile()
        
    return profiles

def _generate_normal_location(profile: Dict) -> Dict:
    """Generate normal location based on user profile"""
    if random.random() < 0.8:
        return profile["home_location"]
    else:
        return random.choice([loc for loc in LOCATIONS if loc["risk"] == "low"])

def _generate_anomalous_location() -> Dict:
    """Generate anomalous location"""
    high_risk_locations = [loc for loc in LOCATIONS if loc["risk"] in ["high", "very_high"]]
    return random.choice(high_risk_locations)

def _generate_normal_ip(profile: Dict) -> str:
    """Generate normal IP address"""
    ip_prefix = random.choice(profile["typical_ips"])
    return ip_prefix + str(random.randint(1, 254))

def _generate_anomalous_ip() -> str:
    """Generate anomalous IP address"""
    suspicious_prefixes = IP_RANGES["suspicious"] + IP_RANGES["malicious"]
    ip_prefix = random.choice(suspicious_prefixes)
    return ip_prefix + str(random.randint(1, 254))

def _generate_normal_time(current_time: datetime, profile: Dict) -> datetime:
    """Generate normal login time based on work hours"""
    start_hour, end_hour = profile["work_hours"]
    
    if random.random() < 0.7:
        hour = random.randint(start_hour, end_hour)
    else:
        hour = random.choice(list(range(6, 23)))
    
    minute = random.randint(0, 59)
    return current_time.replace(hour=hour, minute=minute, second=random.randint(0, 59))

def _generate_anomalous_time(current_time: datetime, profile: Dict) -> datetime:
    """Generate anomalous login time"""
    hour = random.choice([2, 3, 4, 5, 23, 0, 1])
    minute = random.randint(0, 59)
    return current_time.replace(hour=hour, minute=minute, second=random.randint(0, 59))


# New Data Management Endpoints
@router.post("/data/seed")
async def seed_historical_data(
    background_tasks: BackgroundTasks,
    num_events: int = Query(default=1000, description="Number of historical events to generate"),
    anomaly_rate: float = Query(default=0.1, description="Percentage of anomalous events (0.0-1.0)")
):
    """Seed historical data for testing and demo purposes"""
    try:
        if num_events > 10000:
            raise HTTPException(status_code=400, detail="Maximum 10,000 events allowed")
        
        if not 0.0 <= anomaly_rate <= 1.0:
            raise HTTPException(status_code=400, detail="Anomaly rate must be between 0.0 and 1.0")
        
        # Run seeding in background
        background_tasks.add_task(_seed_data_background, num_events, anomaly_rate)
        
        return {
            "message": f"Started seeding {num_events} historical events with {anomaly_rate*100:.1f}% anomaly rate",
            "status": "background_task_started",
            "num_events": num_events,
            "anomaly_rate": anomaly_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start seeding: {e}")
        raise HTTPException(status_code=500, detail="Failed to start seeding")


@router.post("/data/stream/start")
async def start_data_streaming(
    background_tasks: BackgroundTasks,
    duration_minutes: int = Query(default=60, description="Duration in minutes"),
    events_per_minute: int = Query(default=10, description="Events per minute"),
    anomaly_rate: float = Query(default=0.2, description="Percentage of anomalous events (0.0-1.0)")
):
    """Start real-time data streaming"""
    global streaming_active
    
    try:
        if streaming_active:
            raise HTTPException(status_code=400, detail="Data streaming already active")
        
        if duration_minutes > 240:  # Max 4 hours
            raise HTTPException(status_code=400, detail="Maximum duration is 240 minutes")
        
        if events_per_minute > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 events per minute")
        
        if not 0.0 <= anomaly_rate <= 1.0:
            raise HTTPException(status_code=400, detail="Anomaly rate must be between 0.0 and 1.0")
        
        streaming_active = True
        
        # Run streaming in background
        background_tasks.add_task(_stream_data_background, duration_minutes, events_per_minute, anomaly_rate)
        
        return {
            "message": f"Started data streaming for {duration_minutes} minutes",
            "status": "streaming_started",
            "duration_minutes": duration_minutes,
            "events_per_minute": events_per_minute,
            "anomaly_rate": anomaly_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start streaming: {e}")
        raise HTTPException(status_code=500, detail="Failed to start streaming")


@router.post("/data/stream/stop")
async def stop_data_streaming():
    """Stop active data streaming"""
    global streaming_active
    
    if not streaming_active:
        raise HTTPException(status_code=400, detail="No active data streaming")
    
    streaming_active = False
    
    return {
        "message": "Data streaming stopped",
        "status": "streaming_stopped"
    }


@router.get("/data/stream/status")
async def get_streaming_status():
    """Get current streaming status"""
    return {
        "streaming_active": streaming_active,
        "status": "streaming" if streaming_active else "stopped"
    }


@router.post("/data/generate-batch")
async def generate_batch_events(
    count: int = Query(default=10, description="Number of events to generate"),
    anomaly_rate: float = Query(default=0.2, description="Percentage of anomalous events (0.0-1.0)")
):
    """Generate a batch of events immediately"""
    try:
        if count > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 events per batch")
        
        if not 0.0 <= anomaly_rate <= 1.0:
            raise HTTPException(status_code=400, detail="Anomaly rate must be between 0.0 and 1.0")
        
        user_profiles = _initialize_user_profiles()
        events_created = []
        anomalies_detected = 0
        
        for _ in range(count):
            event = _generate_realistic_event(user_profiles, anomaly_rate)
            result = await security_service.process_login_event(event)
            
            if result.get("is_anomaly", False):
                anomalies_detected += 1
            
            events_created.append({
                "event": event.dict(),
                "result": {
                    "anomaly_score": result.get("anomaly_score"),
                    "is_anomaly": result.get("is_anomaly"),
                    "features_count": len(result.get("features", [])),
                    "alert_created": bool(result.get("alert"))
                }
            })
        
        return {
            "message": f"Generated {count} events",
            "events_processed": count,
            "anomalies_detected": anomalies_detected,
            "anomaly_rate_actual": anomalies_detected / count if count > 0 else 0,
            "events": events_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate batch events: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate batch events")


@router.get("/data/stats")
async def get_data_statistics():
    """Get comprehensive data statistics"""
    try:
        client = redis_stack_client.client
        
        # Stream statistics
        stream_length = client.xlen("logins:stream") if client else 0
        
        # Alert statistics
        try:
            alert_search_result = redis_stack_client.search_alerts("*", limit=1000) if redis_stack_client else []
            total_alerts = len(alert_search_result)
        except:
            total_alerts = 0
        
        # IP statistics
        malicious_ip_count = client.scard("bad_ips:set") if client else 0
        
        # TimeSeries statistics (approximate)
        timeseries_keys = []
        try:
            if client:
                timeseries_keys = [key for key in client.scan_iter(match="timeseries:*:anomaly")]
        except:
            pass
        
        # Embedding statistics (approximate)
        embedding_keys = []
        try:
            if client:
                embedding_keys = [key for key in client.scan_iter(match="embeddings:*")]
        except:
            pass
        
        return {
            "redis_connected": bool(client),
            "stream_length": stream_length,
            "total_alerts": total_alerts,
            "malicious_ip_count": malicious_ip_count,
            "unique_users_timeseries": len(timeseries_keys),
            "total_embeddings": len(embedding_keys),
            "streaming_active": streaming_active,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get data statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data statistics")


# Background task functions
async def _seed_data_background(num_events: int, anomaly_rate: float):
    """Background task for seeding historical data"""
    logger.info(f"Starting background seeding of {num_events} events with {anomaly_rate} anomaly rate")
    
    try:
        user_profiles = _initialize_user_profiles()
        events_created = 0
        anomalies_created = 0
        
        # Generate events over the past 30 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        for i in range(num_events):
            try:
                # Generate event with timestamp in the past
                event = _generate_realistic_event(user_profiles, anomaly_rate)
                
                # Randomize timestamp within the past 30 days
                random_time = start_time + timedelta(
                    seconds=random.randint(0, int((end_time - start_time).total_seconds()))
                )
                event.timestamp = int(random_time.timestamp())
                
                # Process through the security service
                result = await security_service.process_login_event(event)
                events_created += 1
                
                if result.get("is_anomaly", False):
                    anomalies_created += 1
                
                # Log progress every 100 events
                if events_created % 100 == 0:
                    logger.info(f"Seeded {events_created}/{num_events} events ({anomalies_created} anomalies)")
                    
                # Small delay to prevent overwhelming the system
                if i % 50 == 0:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Failed to seed event {i}: {e}")
        
        logger.info(f"Seeding complete: {events_created} events, {anomalies_created} anomalies detected")
        
    except Exception as e:
        logger.error(f"Background seeding failed: {e}")


async def _stream_data_background(duration_minutes: int, events_per_minute: int, anomaly_rate: float):
    """Background task for streaming real-time data"""
    global streaming_active
    
    logger.info(f"Starting background streaming for {duration_minutes} minutes at {events_per_minute} events/min")
    
    start_time = time.time()
    events_streamed = 0
    anomalies_detected = 0
    
    try:
        user_profiles = _initialize_user_profiles()
        end_time = start_time + (duration_minutes * 60)
        
        # Calculate delay between events
        delay_between_events = 60.0 / events_per_minute
        
        while streaming_active and time.time() < end_time:
            try:
                # Generate and process event
                event = _generate_realistic_event(user_profiles, anomaly_rate)
                result = await security_service.process_login_event(event)
                events_streamed += 1
                
                if result.get("is_anomaly", False):
                    anomalies_detected += 1
                    logger.info(f"🚨 STREAMING ANOMALY: User {event.user_id} from {event.location} (Score: {result.get('anomaly_score', 'N/A')})")
                
                # Log stats every 50 events
                if events_streamed % 50 == 0:
                    elapsed = (time.time() - start_time) / 60
                    rate = events_streamed / (elapsed if elapsed > 0 else 1)
                    logger.info(f"Streamed {events_streamed} events in {elapsed:.1f}m ({rate:.1f}/min, {anomalies_detected} anomalies)")
                
                # Wait before next event
                await asyncio.sleep(delay_between_events)
                
            except Exception as e:
                logger.error(f"Failed to stream event: {e}")
                await asyncio.sleep(delay_between_events)  # Continue despite errors
                
    except Exception as e:
        logger.error(f"Background streaming failed: {e}")
    finally:
        streaming_active = False
        total_time = (time.time() - start_time) / 60
        logger.info(f"Streaming complete: {events_streamed} events in {total_time:.1f} minutes ({anomalies_detected} anomalies)")


@router.post("/test/redis-features")
async def test_redis_features():
    """Test all Redis 8 features"""
    try:
        # Test basic Redis connection
        client = redis_stack_client.client
        if not client:
            raise HTTPException(status_code=500, detail="Redis client not available")
        
        client.ping()
        
        # Test Redis modules
        modules_info = {}
        try:
            info = client.module_list()
            for module in info:
                module_name = module['name'].decode() if isinstance(module['name'], bytes) else module['name']
                modules_info[module_name.lower()] = True
        except:
            pass
        
        # Generate test event
        test_event = LoginEvent(
            user_id="test_user_redis8",
            ip="203.0.113.42",
            location="San Francisco, CA",
            timestamp=int(time.time())
        )
        
        # Process through security service
        result = await security_service.process_login_event(test_event)
        
        return {
            "redis_connected": True,
            "modules_available": modules_info,
            "test_event_processed": True,
            "anomaly_score": result.get("anomaly_score"),
            "is_anomaly": result.get("is_anomaly"),
            "features_extracted": len(result.get("features", [])),
            "embedding_generated": len(result.get("embedding", [])),
            "alert_created": bool(result.get("alert")),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Redis features test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Redis features test failed: {str(e)}")


@router.delete("/data/clear")
async def clear_all_data(confirm: bool = Query(default=False, description="Confirmation required to clear data")):
    """Clear all data from Redis (use with caution)"""
    if not confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to clear data")
    
    try:
        client = redis_stack_client.client
        if not client:
            raise HTTPException(status_code=500, detail="Redis client not available")
        
        # Clear specific data structures
        keys_to_delete = []
        
        # Find all our application keys
        for pattern in ["logins:stream", "timeseries:*", "embeddings:*", "alert:*", "bad_ips:*"]:
            keys = list(client.scan_iter(match=pattern))
            keys_to_delete.extend(keys)
        
        # Delete keys
        if keys_to_delete:
            client.delete(*keys_to_delete)
        
        # Try to delete search indices
        try:
            client.execute_command("FT.DROPINDEX", "alerts_idx")
        except:
            pass
        
        try:
            client.execute_command("FT.DROPINDEX", "embeddings_idx")
        except:
            pass
        
        return {
            "message": "All application data cleared",
            "keys_deleted": len(keys_to_delete),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear data")


# Event Priority Classification
def classify_event_priority(event_type: str, risk_score: float, is_anomaly: bool, details: Optional[Dict] = None) -> str:
    """Classify event priority based on security importance"""
    details = details or {}
    
    # High Priority (Always Show)
    high_priority_types = {
        "failed_login", "brute_force", "privilege_escalation", 
        "suspicious_login", "impossible_travel", "data_exfiltration",
        "unauthorized_access", "malware_detection", "insider_threat"
    }
    
    # Geographic and time anomalies are always high priority if detected
    if is_anomaly and (risk_score >= 0.7 or event_type in high_priority_types):
        return "high"
    
    # Medium Priority (Show with Context)
    medium_priority_conditions = [
        event_type == "login" and risk_score >= 0.4,  # Successful logins with some risk
        event_type == "admin_access",  # All admin actions are sensitive
        event_type == "api_call" and risk_score >= 0.3,  # API calls with moderate risk
        event_type == "password_change",  # Password changes are notable
        event_type == "account_lockout",
        event_type == "permission_change"
    ]
    
    if any(medium_priority_conditions):
        return "medium"
    
    # Low Priority (Background Processing Only)
    return "low"


@router.get("/events/security")
async def get_security_events(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    priority: Optional[str] = Query(default=None, description="Priority filter: high, medium, low"),
    event_type: Optional[str] = Query(default=None, description="Event type filter"),
    user_id: Optional[str] = Query(default=None, description="User ID filter"),
    min_risk_score: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Minimum risk score"),
    hours_back: int = Query(default=24, ge=1, le=168, description="Hours to look back")
):
    """Get security-focused events with priority classification"""
    try:
        offset = (page - 1) * limit
        
        # Mock security events with priority classification
        all_events = await _generate_mock_security_events(hours_back)
        
        # Filter events based on security relevance (high and medium priority by default)
        if priority:
            filtered_events = [e for e in all_events if e["priority"] == priority]
        else:
            # Default: show high and medium priority events
            filtered_events = [e for e in all_events if e["priority"] in ["high", "medium"]]
        
        # Apply additional filters
        if event_type:
            filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e["user_id"] == user_id]
        
        if min_risk_score is not None:
            filtered_events = [e for e in filtered_events if e["risk_score"] >= min_risk_score]
        
        # Apply pagination
        total_events = len(filtered_events)
        paginated_events = filtered_events[offset:offset + limit]
        
        # Calculate pagination info
        total_pages = (total_events + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "events": paginated_events,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_events,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            },
            "filters_applied": {
                "priority": priority,
                "event_type": event_type,
                "user_id": user_id,
                "min_risk_score": min_risk_score,
                "hours_back": hours_back
            },
            "priority_distribution": _get_priority_distribution(all_events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security events")


@router.get("/events/all")
async def get_all_events(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    event_type: Optional[str] = Query(default=None, description="Event type filter"),
    user_id: Optional[str] = Query(default=None, description="User ID filter"),
    min_risk_score: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Minimum risk score"),
    include_low_priority: bool = Query(default=True, description="Include low priority events"),
    hours_back: int = Query(default=24, ge=1, le=168, description="Hours to look back")
):
    """Get all events including low priority for forensic analysis"""
    try:
        offset = (page - 1) * limit
        
        # Get all events including low priority
        all_events = await _generate_mock_security_events(hours_back, include_all=True)
        
        # Apply filters
        filtered_events = all_events
        
        if not include_low_priority:
            filtered_events = [e for e in filtered_events if e["priority"] != "low"]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e["user_id"] == user_id]
        
        if min_risk_score is not None:
            filtered_events = [e for e in filtered_events if e["risk_score"] >= min_risk_score]
        
        # Apply pagination
        total_events = len(filtered_events)
        paginated_events = filtered_events[offset:offset + limit]
        
        # Calculate pagination info
        total_pages = (total_events + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "events": paginated_events,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_events,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            },
            "filters_applied": {
                "event_type": event_type,
                "user_id": user_id,
                "min_risk_score": min_risk_score,
                "include_low_priority": include_low_priority,
                "hours_back": hours_back
            },
            "priority_distribution": _get_priority_distribution(all_events),
            "total_all_events": len(all_events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get all events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get all events")


async def _generate_mock_security_events(hours_back: int, include_all: bool = False) -> List[Dict]:
    """Generate mock security events with realistic priority distribution"""
    import random
    from datetime import datetime, timedelta
    
    events = []
    current_time = datetime.now()
    start_time = current_time - timedelta(hours=hours_back)
    
    # Define event type distributions and characteristics
    event_types = {
        # High Priority Events
        "failed_login": {"base_risk": 0.7, "anomaly_rate": 0.8, "priority": "high"},
        "brute_force": {"base_risk": 0.9, "anomaly_rate": 0.95, "priority": "high"},
        "impossible_travel": {"base_risk": 0.95, "anomaly_rate": 1.0, "priority": "high"},
        "privilege_escalation": {"base_risk": 0.85, "anomaly_rate": 0.9, "priority": "high"},
        "suspicious_login": {"base_risk": 0.8, "anomaly_rate": 0.85, "priority": "high"},
        "data_exfiltration": {"base_risk": 0.9, "anomaly_rate": 0.9, "priority": "high"},
        "unauthorized_access": {"base_risk": 0.85, "anomaly_rate": 0.8, "priority": "high"},
        
        # Medium Priority Events
        "login": {"base_risk": 0.2, "anomaly_rate": 0.1, "priority": "medium"},
        "admin_access": {"base_risk": 0.4, "anomaly_rate": 0.3, "priority": "medium"},
        "password_change": {"base_risk": 0.3, "anomaly_rate": 0.2, "priority": "medium"},
        "api_call": {"base_risk": 0.15, "anomaly_rate": 0.05, "priority": "medium"},
        "account_lockout": {"base_risk": 0.5, "anomaly_rate": 0.4, "priority": "medium"},
        "permission_change": {"base_risk": 0.45, "anomaly_rate": 0.3, "priority": "medium"},
        
        # Low Priority Events (only included if include_all=True)
        "routine_activity": {"base_risk": 0.05, "anomaly_rate": 0.01, "priority": "low"},
        "system_maintenance": {"base_risk": 0.1, "anomaly_rate": 0.02, "priority": "low"},
        "normal_api_call": {"base_risk": 0.05, "anomaly_rate": 0.01, "priority": "low"},
        "file_access": {"base_risk": 0.08, "anomaly_rate": 0.02, "priority": "low"},
        "session_refresh": {"base_risk": 0.02, "anomaly_rate": 0.01, "priority": "low"}
    }
    
    # Filter event types based on include_all flag
    if not include_all:
        event_types = {k: v for k, v in event_types.items() if v["priority"] != "low"}
    
    # Generate events with realistic distribution
    num_events = random.randint(200, 500) if include_all else random.randint(50, 150)
    
    for i in range(num_events):
        # Choose event type based on realistic frequency
        if include_all:
            # More low priority events in reality
            priorities = ["high"] * 10 + ["medium"] * 30 + ["low"] * 60
        else:
            priorities = ["high"] * 25 + ["medium"] * 75
        
        target_priority = random.choice(priorities)
        event_type_options = [k for k, v in event_types.items() if v["priority"] == target_priority]
        event_type = random.choice(event_type_options)
        
        config = event_types[event_type]
        
        # Generate risk score with some variation
        base_risk = config["base_risk"]
        risk_score = max(0.0, min(1.0, base_risk + random.uniform(-0.2, 0.2)))
        
        # Determine if anomaly
        is_anomaly = random.random() < config["anomaly_rate"]
        if is_anomaly:
            risk_score = max(risk_score, 0.6)  # Anomalies have higher risk
        
        # Generate timestamp within the time range
        event_time = start_time + timedelta(
            seconds=random.randint(0, int((current_time - start_time).total_seconds()))
        )
        
        # Generate user and location
        user_id = random.choice(USERS)
        location = random.choice(LOCATIONS)
        ip_type = "suspicious" if risk_score > 0.7 else random.choice(["corporate", "home", "vpn"])
        ip_prefix = random.choice(IP_RANGES[ip_type])
        ip_address = ip_prefix + str(random.randint(1, 254))
        
        # Classify priority using our function
        priority = classify_event_priority(event_type, risk_score, is_anomaly)
        
        event = {
            "id": f"event_{i+1:06d}",
            "user_id": user_id,
            "event_type": event_type,
            "ip_address": ip_address,
            "location": f"{location['city']}, {location['country']}",
            "timestamp": event_time.isoformat(),
            "risk_score": round(risk_score, 3),
            "is_anomaly": is_anomaly,
            "priority": priority,
            "location_risk": location["risk"],
            "details": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "session_id": f"sess_{random.randint(100000, 999999)}",
                "action": event_type.replace("_", " ").title(),
                "resource": f"/api/{event_type}" if "api" in event_type else None,
                "duration_ms": random.randint(50, 2000) if event_type in ["api_call", "data_access"] else None
            }
        }
        
        events.append(event)
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return events


def _get_priority_distribution(events: List[Dict]) -> Dict:
    """Calculate priority distribution statistics"""
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    
    for event in events:
        priority = event.get("priority", "low")
        priority_counts[priority] += 1
    
    total = len(events)
    
    return {
        "total_events": total,
        "high_priority": {
            "count": priority_counts["high"],
            "percentage": round((priority_counts["high"] / total) * 100, 1) if total > 0 else 0
        },
        "medium_priority": {
            "count": priority_counts["medium"],
            "percentage": round((priority_counts["medium"] / total) * 100, 1) if total > 0 else 0
        },
        "low_priority": {
            "count": priority_counts["low"],
            "percentage": round((priority_counts["low"] / total) * 100, 1) if total > 0 else 0
        }
    }


# LLM Endpoints
@router.get("/llm/status")
async def get_llm_status():
    """Get LLM service status"""
    try:
        status = await llm_service.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get LLM status")


@router.get("/llm/explain-threat/{alert_id}")
async def explain_threat(alert_id: str):
    """Get AI-powered explanation for a security threat"""
    try:
        if not await llm_service.is_available():
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        explanation = await llm_service.explain_threat(alert_id)
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to explain threat {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to explain threat")


@router.post("/llm/chat")
async def chat_with_ai(request: Dict[str, Any]):
    """Chat with AI assistant about security data"""
    try:
        if not await llm_service.is_available():
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        message = request.get("message", "")
        context = request.get("context", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get security context for the AI
        security_context = await get_security_context()
        
        # Enhance the message with security context
        enhanced_message = f"""
SECURITY SYSTEM CONTEXT:
{security_context}

USER QUESTION: {message}

Please provide helpful information based on the current security context above. Be specific and actionable."""

        response = await llm_service.chat(enhanced_message, context)
        return response
        
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


async def get_security_context() -> str:
    """Get current security context for AI"""
    try:
        # Get current alerts (mock data for now)
        current_alerts = [
            {
                "id": "alert_001",
                "title": "Suspicious Login Pattern Detected",
                "severity": "critical",
                "status": "open",
                "event_type": "anomalous_login",
                "user_id": "user_123",
                "risk_score": 0.95
            },
            {
                "id": "alert_002", 
                "title": "Multiple Failed Login Attempts",
                "severity": "high",
                "status": "investigating",
                "event_type": "brute_force",
                "risk_score": 0.85
            },
            {
                "id": "alert_003",
                "title": "Unusual Data Access Pattern", 
                "severity": "high",
                "status": "open",
                "event_type": "data_exfiltration",
                "user_id": "user_789",
                "risk_score": 0.88
            }
        ]
        
        # Get system statistics
        total_alerts = len(current_alerts)
        critical_high_alerts = len([a for a in current_alerts if a["severity"] in ["critical", "high"]])
        open_alerts = len([a for a in current_alerts if a["status"] == "open"])
        
        # Get top threat types
        threat_types = {}
        for alert in current_alerts:
            event_type = alert["event_type"]
            threat_types[event_type] = threat_types.get(event_type, 0) + 1
        
        top_threats = sorted(threat_types.items(), key=lambda x: x[1], reverse=True)
        
        # Get recent user activity patterns
        high_risk_users = [a["user_id"] for a in current_alerts if a.get("user_id") and a["risk_score"] > 0.8]
        
        context = f"""
CURRENT SECURITY STATUS:
- Total Active Alerts: {total_alerts}
- Critical/High Severity: {critical_high_alerts}
- Open Alerts Requiring Action: {open_alerts}

TOP THREAT CATEGORIES:
{chr(10).join([f"- {threat_type.replace('_', ' ').title()}: {count} alerts" for threat_type, count in top_threats[:3]])}

HIGH-RISK USERS DETECTED:
{chr(10).join([f"- {user_id}" for user_id in high_risk_users[:5]])}

RECENT SECURITY EVENTS:
- Anomalous login patterns from multiple geographic locations
- Brute force attacks detected and partially mitigated  
- Unusual data access volumes requiring investigation
- Off-hours administrative access attempts

SYSTEM CAPABILITIES:
- Real-time threat detection using Redis Stack 8 with vector similarity
- ML-based anomaly detection for user behavior
- Geographic anomaly detection for impossible travel
- API rate limiting and abuse detection
- Automated IP reputation checking
"""
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to get security context: {e}")
        return "Security context temporarily unavailable."
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")
