#!/usr/bin/env python3
"""
Redis Native Data Streamer for Rediguard
Directly streams data to Redis without external dependencies
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Import our Redis Stack client
from app.core.redis_stack import redis_stack_client
from app.models import LoginEvent
from app.services.security_service import SecurityService

class RedisNativeStreamer:
    """Stream data directly to Redis using native Redis operations"""
    
    def __init__(self):
        self.security_service = SecurityService()
        self.users = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry"]
        self.locations = [
            "New York, US", "London, UK", "Tokyo, JP", "Sydney, AU",
            "Berlin, DE", "Toronto, CA", "Mumbai, IN", "São Paulo, BR",
            "Moscow, RU", "Beijing, CN", "Lagos, NG", "Tehran, IR"
        ]
        
    def generate_event(self, anomalous: bool = False) -> LoginEvent:
        """Generate a login event"""
        user = random.choice(self.users)
        
        if anomalous:
            # Anomalous patterns
            ip = f"{random.randint(100, 255)}.{random.randint(100, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            location = random.choice(self.locations[-4:])  # High-risk locations
            # Unusual time
            hour = random.choice([2, 3, 4, 23, 0, 1])
        else:
            # Normal patterns
            ip = f"192.168.{random.randint(1, 10)}.{random.randint(1, 100)}"
            location = random.choice(self.locations[:6])  # Low-risk locations
            # Business hours
            hour = random.randint(9, 17)
        
        timestamp = datetime.now().replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return LoginEvent(
            user_id=user,
            ip=ip,
            location=location,
            timestamp=int(timestamp.timestamp())
        )
    
    async def seed_bulk_data(self, num_events: int = 500):
        """Seed bulk data efficiently"""
        print(f"🌱 Seeding {num_events} events to Redis...")
        
        successful = 0
        anomalies = 0
        
        # Process in batches for efficiency
        batch_size = 50
        
        for batch_start in range(0, num_events, batch_size):
            batch_end = min(batch_start + batch_size, num_events)
            batch_events = []
            
            # Generate batch
            for i in range(batch_start, batch_end):
                is_anomalous = random.random() < 0.15  # 15% anomaly rate
                event = self.generate_event(is_anomalous)
                
                # Vary timestamp over past 7 days
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                past_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
                event.timestamp = int(past_time.timestamp())
                
                batch_events.append(event)
            
            # Process batch
            for event in batch_events:
                try:
                    result = await self.security_service.process_login_event(event)
                    successful += 1
                    
                    if result.get("is_anomaly", False):
                        anomalies += 1
                        
                except Exception as e:
                    print(f"❌ Failed to process event: {e}")
            
            # Progress update
            print(f"   📊 Processed {batch_end}/{num_events} events ({anomalies} anomalies detected)")
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        print(f"✅ Bulk seeding complete: {successful} events, {anomalies} anomalies")
        await self.show_redis_stats()
    
    async def stream_realtime(self, duration_minutes: int = 10, events_per_minute: int = 12):
        """Stream real-time events"""
        print(f"🚀 Streaming for {duration_minutes} minutes at {events_per_minute} events/minute...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        total_events = 0
        total_anomalies = 0
        
        try:
            while time.time() < end_time:
                # Generate events for this interval
                events_this_round = events_per_minute // 2  # Process in smaller chunks
                
                for _ in range(events_this_round):
                    is_anomalous = random.random() < 0.25  # Higher rate for demo
                    event = self.generate_event(is_anomalous)
                    
                    try:
                        result = await self.security_service.process_login_event(event)
                        total_events += 1
                        
                        if result.get("is_anomaly", False):
                            total_anomalies += 1
                            score = result.get("anomaly_score", 0)
                            print(f"🚨 ANOMALY: {event.user_id} from {event.location} (Score: {score:.3f})")
                        
                    except Exception as e:
                        print(f"❌ Stream error: {e}")
                
                # Status update
                elapsed = (time.time() - start_time) / 60
                rate = total_events / elapsed if elapsed > 0 else 0
                print(f"📈 Streaming: {total_events} events ({rate:.1f}/min) - {total_anomalies} anomalies")
                
                # Wait before next batch
                await asyncio.sleep(30)  # 30 second intervals
                
        except KeyboardInterrupt:
            print("🛑 Streaming interrupted")
        
        total_time = (time.time() - start_time) / 60
        print(f"✅ Streaming complete: {total_events} events in {total_time:.1f}m")
        await self.show_redis_stats()
    
    async def show_redis_stats(self):
        """Show Redis statistics"""
        try:
            # Get Redis client
            client = redis_stack_client.client
            
            # Stream statistics
            stream_length = client.xlen("logins:stream") if client else 0
            
            # Memory usage
            memory_info = client.memory_usage("logins:stream") if client else 0
            memory_mb = memory_info / 1024 / 1024 if memory_info else 0
            
            # Alert count (using search)
            try:
                alert_results = redis_stack_client.search_alerts("*", limit=1000)
                alert_count = len(alert_results)
            except:
                alert_count = 0
            
            print(f"\n📊 Redis Statistics:")
            print(f"   🔄 Stream Length: {stream_length} events")
            print(f"   🚨 Alerts Created: {alert_count}")
            print(f"   💾 Stream Memory: {memory_mb:.2f} MB")
            
            # Try to get embeddings count
            try:
                # Use vector search to estimate embeddings count
                test_embedding = [0.0] * 128  # 128-dimensional zero vector
                embedding_results = redis_stack_client.vector_search(test_embedding, limit=1000)
                embedding_count = len(embedding_results)
                print(f"   🧠 Embeddings: {embedding_count} vectors")
            except:
                print(f"   🧠 Embeddings: N/A")
            
        except Exception as e:
            print(f"❌ Failed to get Redis stats: {e}")
    
    async def test_redis_features(self):
        """Test Redis 8 features"""
        print("🔍 Testing Redis 8 Features...")
        
        try:
            # Test connection
            client = redis_stack_client.client
            if client:
                ping_result = client.ping()
                print(f"✅ Redis Connection: {ping_result}")
            else:
                print("❌ Redis Connection: No client available")
            
            # Test modules
            modules = redis_stack_client._modules_available
            print(f"✅ Available Modules:")
            for module, available in modules.items():
                status = "✅" if available else "❌"
                print(f"   {status} {module.title()}: {available}")
            
            # Test TimeSeries
            if modules.get("timeseries"):
                try:
                    ts_key = "test:timeseries"
                    redis_stack_client.add_anomaly_score("test_user", 0.75)
                    print("✅ TimeSeries: Working")
                except Exception as e:
                    print(f"❌ TimeSeries: {e}")
            
            # Test JSON
            if modules.get("json"):
                try:
                    test_doc = {"test": "value", "timestamp": time.time()}
                    redis_stack_client.store_alert_json("test:alert", test_doc)
                    print("✅ JSON: Working")
                except Exception as e:
                    print(f"❌ JSON: {e}")
            
            # Test Search
            if modules.get("search"):
                try:
                    results = redis_stack_client.search_alerts("*", limit=1)
                    print(f"✅ Search: Working ({len(results)} results)")
                except Exception as e:
                    print(f"❌ Search: {e}")
            
        except Exception as e:
            print(f"❌ Redis features test failed: {e}")

async def main():
    """Main function"""
    print("🚀 Redis Native Data Streamer for Rediguard")
    print("=" * 60)
    
    # Connect to Redis
    try:
        redis_stack_client.connect()
        print("✅ Connected to Redis Stack")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return
    
    streamer = RedisNativeStreamer()
    
    try:
        while True:
            print("\nChoose an option:")
            print("1. Test Redis 8 features")
            print("2. Show current Redis stats")
            print("3. Seed 100 historical events")
            print("4. Seed 500 historical events")
            print("5. Stream for 5 minutes")
            print("6. Stream for 15 minutes")
            print("7. Bulk seed 1000 + Stream 10 minutes")
            print("8. Exit")
            
            choice = input("\nEnter choice (1-8): ").strip()
            
            if choice == "1":
                await streamer.test_redis_features()
            elif choice == "2":
                await streamer.show_redis_stats()
            elif choice == "3":
                await streamer.seed_bulk_data(100)
            elif choice == "4":
                await streamer.seed_bulk_data(500)
            elif choice == "5":
                await streamer.stream_realtime(5, 12)
            elif choice == "6":
                await streamer.stream_realtime(15, 12)
            elif choice == "7":
                await streamer.seed_bulk_data(1000)
                print("\n" + "="*40)
                await streamer.stream_realtime(10, 12)
            elif choice == "8":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
                
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        redis_stack_client.close()
        print("🔒 Redis connection closed")

if __name__ == "__main__":
    asyncio.run(main())
