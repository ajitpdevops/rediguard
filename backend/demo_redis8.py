#!/usr/bin/env python3
"""Comprehensive Redis 8 + AI Demo for Rediguard"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict

from app.core.redis_stack import redis_stack_client
from app.services.security_service import security_service
from app.services.ai_service import ai_service
from app.models import LoginEvent


async def demo_redis8_features():
    """Comprehensive demo of Redis 8 features in Rediguard"""
    print("🚀 Rediguard Redis 8 + AI Demo")
    print("=" * 50)
    
    try:
        # Connect to Redis Stack
        print("📡 Connecting to Redis Stack...")
        redis_stack_client.connect()
        print(f"✅ Connected! Modules available: {redis_stack_client._modules_available}")
        
        # Demo 1: Real-time login event processing with Streams
        print("\n1️⃣ Demo: Real-time Login Event Processing (Redis Streams)")
        print("-" * 50)
        
        demo_events = [
            {"user": "alice", "ip": "192.168.1.100", "location": "New York"},
            {"user": "bob", "ip": "10.0.0.50", "location": "London"},
            {"user": "charlie", "ip": "203.0.113.1", "location": "Tokyo"},
            {"user": "alice", "ip": "185.220.101.1", "location": "Moscow"},  # Suspicious
        ]
        
        alerts = []
        for event_data in demo_events:
            event = LoginEvent(
                user_id=event_data["user"],
                ip=event_data["ip"],
                location=event_data["location"],
                timestamp=datetime.now()
            )
            
            print(f"  Processing: {event.user_id} from {event.ip} ({event.location})")
            alert = await security_service.process_login_event(event)
            alerts.append(alert)
            print(f"    → Alert Score: {alert.score:.3f}, Malicious IP: {alert.is_malicious_ip}")
        
        # Demo 2: TimeSeries anomaly tracking
        print("\n2️⃣ Demo: Anomaly Score TimeSeries (Redis TimeSeries)")
        print("-" * 50)
        
        for user in ["alice", "bob", "charlie"]:
            history = await security_service.get_user_anomaly_history(user, hours=1)
            print(f"  {user}: {len(history)} anomaly scores tracked")
            if history:
                latest = history[-1]
                print(f"    Latest: {latest['score']:.3f} at {latest['timestamp']}")
        
        # Demo 3: JSON document search
        print("\n3️⃣ Demo: Alert Search (Redis Search + JSON)")
        print("-" * 50)
        
        # Search high-risk alerts
        high_risk = await security_service.get_high_risk_alerts(threshold=0.5)
        print(f"  High-risk alerts (>0.5): {len(high_risk)}")
        
        # Search by user
        alice_alerts = await security_service.get_user_alerts("alice")
        print(f"  Alice's alerts: {len(alice_alerts)}")
        
        # Demo 4: Bloom filter IP reputation
        print("\n4️⃣ Demo: IP Reputation (Redis Bloom Filter)")
        print("-" * 50)
        
        test_ips = ["192.168.1.100", "8.8.8.8", "185.220.101.1", "1.1.1.1"]
        for ip in test_ips:
            reputation = await security_service.check_ip_reputation(ip)
            status = "🔴 MALICIOUS" if reputation["is_malicious"] else "🟢 CLEAN"
            print(f"  {ip}: {status}")
        
        # Demo 5: Vector similarity search
        print("\n5️⃣ Demo: Behavior Similarity (Vector Search)")
        print("-" * 50)
        
        for user in ["alice", "bob"]:
            similar = await security_service.find_similar_behaviors(user, limit=3)
            print(f"  {user} similar behaviors: {len(similar)}")
            for sim in similar[:2]:
                print(f"    → User: {sim.get('user_id', 'unknown')}, Distance: {sim.get('distance', 0):.3f}")
        
        # Demo 6: Real-time stream processing
        print("\n6️⃣ Demo: Real-time Event Stream Processing")
        print("-" * 50)
        
        # Read events from stream
        events = await security_service.get_real_time_events(count=5)
        print(f"  Processed {len(events)} real-time events")
        for event in events[:3]:
            fields = event.get("fields", {})
            print(f"    → {fields.get('user_id', 'unknown')} from {fields.get('ip', 'unknown')}")
        
        # Demo 7: AI-powered analysis
        print("\n7️⃣ Demo: AI Analysis Integration")
        print("-" * 50)
        
        # Analyze a suspicious event
        suspicious_event = LoginEvent(
            user_id="alice",
            ip="198.51.100.1",  # Different country
            location="Beijing",
            timestamp=datetime.now()
        )
        
        print(f"  Analyzing suspicious login: {suspicious_event.user_id} from {suspicious_event.location}")
        analysis = await ai_service.analyze_login_behavior(suspicious_event)
        print(f"    AI Score: {analysis.anomaly_score:.3f}")
        print(f"    Features: {len(analysis.details.get('features', []))} behavioral features")
        print(f"    Embedding: {len(getattr(analysis, 'embedding', []))} dimensions")
        
        # Demo 8: System statistics
        print("\n8️⃣ Demo: System Statistics")
        print("-" * 50)
        
        stats = await security_service.get_system_stats()
        print(f"  Redis connected: {stats.get('redis_connected', False)}")
        print(f"  Redis version: {stats.get('redis_version', 'unknown')}")
        print(f"  Memory usage: {stats.get('used_memory_human', 'unknown')}")
        print(f"  Connected clients: {stats.get('connected_clients', 0)}")
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("🔗 Access RedisInsight at: http://localhost:8001")
        print("📊 API Documentation at: http://localhost:8000/docs")
        print("💡 All Redis 8 features are now active and ready for production scaling!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        redis_stack_client.close()


if __name__ == "__main__":
    asyncio.run(demo_redis8_features())
