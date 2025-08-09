#!/usr/bin/env python3
"""
Data Seeding and Streaming Script for Rediguard
Generates realistic security events and streams them to Redis 8 for testing
"""

import asyncio
import random
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests

from app.models import LoginEvent
from app.services.security_service import SecurityService
from app.core.redis_stack import redis_stack_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
STREAM_DELAY = 2.0  # seconds between events
BATCH_SIZE = 10  # events per batch

# Realistic data sets
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

# IP address ranges by risk level
IP_RANGES = {
    "corporate": ["192.168.1.", "10.0.0.", "172.16.0."],
    "home": ["203.0.113.", "198.51.100.", "192.0.2."],
    "vpn": ["185.220.", "91.207.", "104.244."],
    "suspicious": ["123.456.", "45.67.", "89.12."],
    "malicious": ["666.13.", "31.13.", "172.245."]
}

class DataStreamer:
    """Real-time data streaming for Redis 8 testing"""
    
    def __init__(self):
        self.security_service = SecurityService()
        self.user_profiles = self._initialize_user_profiles()
        self.running = False
        
    def _initialize_user_profiles(self) -> Dict[str, Dict]:
        """Create user behavior profiles"""
        profiles = {}
        
        for user in USERS:
            # Assign typical locations and work hours
            home_location = random.choice([loc for loc in LOCATIONS if loc["risk"] == "low"])
            work_hours = (random.randint(8, 10), random.randint(17, 19))
            
            profiles[user] = {
                "home_location": home_location,
                "work_hours": work_hours,
                "typical_ips": random.sample(IP_RANGES["corporate"] + IP_RANGES["home"], 3),
                "login_frequency": random.uniform(0.5, 3.0),  # logins per hour
                "risk_tolerance": random.choice(["low", "medium", "high"])
            }
            
        return profiles
    
    def _generate_realistic_event(self, anomaly_chance: float = 0.15) -> LoginEvent:
        """Generate a realistic login event"""
        user = random.choice(USERS)
        profile = self.user_profiles[user]
        current_time = datetime.now()
        
        # Determine if this should be an anomalous event
        is_anomaly = random.random() < anomaly_chance
        
        if is_anomaly:
            # Generate anomalous behavior
            location = self._generate_anomalous_location(profile)
            ip = self._generate_anomalous_ip()
            timestamp = self._generate_anomalous_time(current_time, profile)
        else:
            # Generate normal behavior
            location = self._generate_normal_location(profile)
            ip = self._generate_normal_ip(profile)
            timestamp = self._generate_normal_time(current_time, profile)
        
        return LoginEvent(
            user_id=user,
            ip=ip,
            location=f"{location['city']}, {location['country']}",
            timestamp=int(timestamp.timestamp())
        )
    
    def _generate_normal_location(self, profile: Dict) -> Dict:
        """Generate normal location based on user profile"""
        # 80% chance of home location, 20% chance of nearby low-risk location
        if random.random() < 0.8:
            return profile["home_location"]
        else:
            return random.choice([loc for loc in LOCATIONS if loc["risk"] == "low"])
    
    def _generate_anomalous_location(self, profile: Dict) -> Dict:
        """Generate anomalous location"""
        # High-risk locations or very distant locations
        high_risk_locations = [loc for loc in LOCATIONS if loc["risk"] in ["high", "very_high"]]
        return random.choice(high_risk_locations)
    
    def _generate_normal_ip(self, profile: Dict) -> str:
        """Generate normal IP address"""
        ip_prefix = random.choice(profile["typical_ips"])
        return ip_prefix + str(random.randint(1, 254))
    
    def _generate_anomalous_ip(self) -> str:
        """Generate anomalous IP address"""
        suspicious_prefixes = IP_RANGES["suspicious"] + IP_RANGES["malicious"]
        ip_prefix = random.choice(suspicious_prefixes)
        return ip_prefix + str(random.randint(1, 254))
    
    def _generate_normal_time(self, current_time: datetime, profile: Dict) -> datetime:
        """Generate normal login time based on work hours"""
        start_hour, end_hour = profile["work_hours"]
        
        # 70% chance within work hours, 30% chance within reasonable hours
        if random.random() < 0.7:
            # Work hours
            hour = random.randint(start_hour, end_hour)
        else:
            # Extended reasonable hours (6 AM to 11 PM)
            hour = random.choice(list(range(6, 23)))
        
        # Random time within the hour
        minute = random.randint(0, 59)
        
        return current_time.replace(hour=hour, minute=minute, second=random.randint(0, 59))
    
    def _generate_anomalous_time(self, current_time: datetime, profile: Dict) -> datetime:
        """Generate anomalous login time"""
        # Very early morning or very late night
        hour = random.choice([2, 3, 4, 5, 23, 0, 1])
        minute = random.randint(0, 59)
        
        return current_time.replace(hour=hour, minute=minute, second=random.randint(0, 59))
    
    async def seed_historical_data(self, num_events: int = 1000):
        """Seed historical data for testing"""
        logger.info(f"🌱 Seeding {num_events} historical events...")
        
        events_created = 0
        anomalies_created = 0
        
        # Generate events over the past 30 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        for i in range(num_events):
            # Generate event with timestamp in the past
            event = self._generate_realistic_event(anomaly_chance=0.1)
            
            # Randomize timestamp within the past 30 days
            random_time = start_time + timedelta(
                seconds=random.randint(0, int((end_time - start_time).total_seconds()))
            )
            event.timestamp = int(random_time.timestamp())
            
            try:
                # Process through the security service
                result = await self.security_service.process_login_event(event)
                events_created += 1
                
                if result.get("is_anomaly", False):
                    anomalies_created += 1
                
                # Log progress every 100 events
                if events_created % 100 == 0:
                    logger.info(f"   📊 Created {events_created}/{num_events} events ({anomalies_created} anomalies)")
                    
            except Exception as e:
                logger.error(f"Failed to create event {i}: {e}")
        
        logger.info(f"✅ Seeding complete: {events_created} events, {anomalies_created} anomalies detected")
        
        # Generate some summary statistics
        await self._log_seeding_stats()
    
    async def stream_realtime_data(self, duration_minutes: int = 60):
        """Stream real-time data for testing"""
        logger.info(f"🚀 Starting real-time data stream for {duration_minutes} minutes...")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        events_streamed = 0
        anomalies_detected = 0
        
        try:
            while self.running and time.time() < end_time:
                # Generate batch of events
                batch_events = []
                
                for _ in range(BATCH_SIZE):
                    event = self._generate_realistic_event(anomaly_chance=0.2)  # Higher anomaly rate for testing
                    batch_events.append(event)
                
                # Process batch
                for event in batch_events:
                    try:
                        result = await self.security_service.process_login_event(event)
                        events_streamed += 1
                        
                        if result.get("is_anomaly", False):
                            anomalies_detected += 1
                            logger.info(f"🚨 ANOMALY: User {event.user_id} from {event.location} (Score: {result.get('anomaly_score', 'N/A')})")
                        
                        # Log real-time stats
                        if events_streamed % 50 == 0:
                            elapsed = (time.time() - start_time) / 60
                            rate = events_streamed / (elapsed if elapsed > 0 else 1)
                            logger.info(f"📈 Streamed {events_streamed} events in {elapsed:.1f}m ({rate:.1f}/min, {anomalies_detected} anomalies)")
                            
                    except Exception as e:
                        logger.error(f"Failed to process event: {e}")
                
                # Wait before next batch
                await asyncio.sleep(STREAM_DELAY)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stream interrupted by user")
        finally:
            self.running = False
            
        total_time = (time.time() - start_time) / 60
        logger.info(f"✅ Streaming complete: {events_streamed} events in {total_time:.1f} minutes ({anomalies_detected} anomalies)")
    
    async def _log_seeding_stats(self):
        """Log statistics about seeded data"""
        try:
            # Get Redis info
            redis_info = await self.security_service.get_redis_info()
            
            logger.info("📊 Seeding Statistics:")
            logger.info(f"   🔄 Stream Length: {redis_info.get('stream_length', 'N/A')}")
            logger.info(f"   🚨 Total Alerts: {redis_info.get('total_alerts', 'N/A')}")
            logger.info(f"   🌐 Malicious IPs: {redis_info.get('malicious_ips', 'N/A')}")
            logger.info(f"   🧠 Embeddings: {redis_info.get('embeddings_count', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Failed to get seeding stats: {e}")
    
    def stop_streaming(self):
        """Stop the real-time streaming"""
        self.running = False

async def main():
    """Main function to run seeding and streaming"""
    logger.info("🚀 Rediguard Data Seeding and Streaming Tool")
    logger.info("=" * 60)
    
    # Initialize Redis Stack connection
    try:
        redis_stack_client.connect()
        logger.info("✅ Connected to Redis Stack")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis Stack: {e}")
        return
    
    streamer = DataStreamer()
    
    try:
        # Menu for user choice
        print("\nChoose an option:")
        print("1. Seed historical data (1000 events)")
        print("2. Stream real-time data (60 minutes)")
        print("3. Seed + Stream (1000 historical + 60 min streaming)")
        print("4. Quick test (100 events + 5 min streaming)")
        print("5. Custom configuration")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            await streamer.seed_historical_data(1000)
            
        elif choice == "2":
            await streamer.stream_realtime_data(60)
            
        elif choice == "3":
            await streamer.seed_historical_data(1000)
            logger.info("🔄 Starting real-time streaming...")
            await streamer.stream_realtime_data(60)
            
        elif choice == "4":
            await streamer.seed_historical_data(100)
            logger.info("🔄 Starting quick streaming test...")
            await streamer.stream_realtime_data(5)
            
        elif choice == "5":
            num_historical = int(input("Number of historical events to seed: "))
            stream_duration = int(input("Streaming duration in minutes: "))
            
            if num_historical > 0:
                await streamer.seed_historical_data(num_historical)
            
            if stream_duration > 0:
                await streamer.stream_realtime_data(stream_duration)
        
        else:
            logger.error("Invalid choice")
            return
            
    except KeyboardInterrupt:
        logger.info("🛑 Operation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error during operation: {e}")
    finally:
        streamer.stop_streaming()
        redis_stack_client.close()
        logger.info("🔒 Redis Stack connection closed")

if __name__ == "__main__":
    asyncio.run(main())
