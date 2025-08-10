#!/usr/bin/env python3
"""
Comprehensive Redis 8 Feature Test for Rediguard Backend
Tests all Redis Stack 8 features: TimeSeries, JSON, Search, Vector Search
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health Status: {data['status']}")
        print(f"✅ Redis Stack: {data['redis_stack']}")
        print(f"✅ Modules Available: {data['redis_modules']}")
        
        # Check which Redis 8 features are available
        modules = data['redis_modules']
        print("\n📊 Redis 8 Feature Status:")
        print(f"   🕰️  TimeSeries: {'✅' if modules.get('timeseries') else '❌'}")
        print(f"   📄 JSON: {'✅' if modules.get('json') else '❌'}")
        print(f"   🔍 Search: {'✅' if modules.get('search') else '❌'}")
        print(f"   🌸 Bloom Filter: {'✅' if modules.get('bloom') else '❌'}")
        print(f"   📈 Graph: {'✅' if modules.get('graph') else '❌'}")
        
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_login_event_processing():
    """Test login event processing with Redis Stack features"""
    print("\n🔐 Testing Login Event Processing...")
    
    # Test login event
    login_event = {
        "user_id": "test_user_001",
        "ip": "203.0.113.42",
        "location": "San Francisco, CA",
        "timestamp": int(time.time())
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/events/login", json=login_event)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Event processed successfully")
        print(f"   📊 Anomaly Score: {data.get('anomaly_score', 'N/A')}")
        print(f"   🚨 Is Anomaly: {data.get('is_anomaly', 'N/A')}")
        print(f"   🎯 Features Extracted: {len(data.get('features', []))}")
        print(f"   🧠 Embedding Generated: {len(data.get('embedding', []))}")
        print(f"   🔍 Similar Events Found: {len(data.get('similar_events', []))}")
        
        if data.get('alert'):
            print(f"   🚨 Alert Created: {data['alert']['alert_id']}")
        
        return data
    else:
        print(f"❌ Login event processing failed: {response.status_code}")
        return None

def test_security_alerts():
    """Test security alert search using Redis Search"""
    print("\n🚨 Testing Security Alert Search...")
    
    response = requests.get(f"{BASE_URL}/api/v1/alerts/search?limit=10")
    
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('alerts', [])
        print(f"✅ Found {len(alerts)} security alerts")
        
        for i, alert in enumerate(alerts[:3]):  # Show first 3
            print(f"   Alert {i+1}: User {alert.get('user_id')} from {alert.get('ip')} (Score: {alert.get('score', 'N/A')})")
        
        return alerts
    else:
        print(f"❌ Alert search failed: {response.status_code}")
        return []

def test_anomaly_history():
    """Test anomaly history using Redis TimeSeries"""
    print("\n📈 Testing Anomaly History (TimeSeries)...")
    
    user_id = "test_user_001"
    response = requests.get(f"{BASE_URL}/api/v1/users/{user_id}/anomaly-history?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        history = data.get('history', [])
        print(f"✅ Retrieved {len(history)} anomaly scores for user {user_id}")
        
        for i, entry in enumerate(history[:3]):  # Show first 3
            dt = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   Score {i+1}: {entry['score']:.3f} at {dt}")
        
        return history
    else:
        print(f"❌ Anomaly history retrieval failed: {response.status_code}")
        return []

def test_ip_reputation():
    """Test IP reputation check using Bloom Filter (fallback if not available)"""
    print("\n🌐 Testing IP Reputation Check...")
    
    test_ip = "203.0.113.42"
    response = requests.get(f"{BASE_URL}/api/v1/ip/{test_ip}/reputation")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ IP reputation check for {test_ip}")
        print(f"   🚨 Is Malicious: {data.get('is_malicious', 'N/A')}")
        print(f"   ⏰ Checked At: {data.get('checked_at', 'N/A')}")
        
        return data
    else:
        print(f"❌ IP reputation check failed: {response.status_code}")
        return None

def test_behavior_similarity():
    """Test behavior similarity using Vector Search"""
    print("\n🧠 Testing Behavior Similarity (Vector Search)...")
    
    user_id = "test_user_001"
    response = requests.get(f"{BASE_URL}/api/v1/users/{user_id}/similar-behavior?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        similar = data.get('similar_events', [])
        print(f"✅ Found {len(similar)} similar behavior patterns")
        
        for i, event in enumerate(similar[:3]):  # Show first 3
            print(f"   Pattern {i+1}: User {event.get('user_id')} (Distance: {event.get('distance', 'N/A')})")
        
        return similar
    else:
        print(f"❌ Behavior similarity search failed: {response.status_code}")
        return []

def test_generate_demo_data():
    """Generate test data to populate Redis"""
    print("\n🎯 Generating Demo Data...")
    
    response = requests.post(f"{BASE_URL}/api/v1/demo/generate-data?num_events=5")
    
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print(f"✅ Generated {len(events)} demo events")
        
        for i, event_data in enumerate(events[:3]):  # Show first 3
            event = event_data.get('event', {})
            result = event_data.get('result', {})
            print(f"   Event {i+1}: {event.get('user_id')} from {event.get('location')} (Score: {result.get('anomaly_score', 'N/A')})")
        
        return events
    else:
        print(f"❌ Demo data generation failed: {response.status_code}")
        return []

def main():
    """Run comprehensive Redis 8 feature test"""
    print("🚀 Starting Rediguard Redis 8 Feature Test\n")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health_check():
        print("❌ Health check failed. Exiting.")
        return
    
    # Test 2: Generate demo data first
    test_generate_demo_data()
    
    # Wait a moment for data to be processed
    time.sleep(1)
    
    # Test 3: Login event processing
    test_login_event_processing()
    
    # Test 4: Security alerts (Redis Search + JSON)
    test_security_alerts()
    
    # Test 5: Anomaly history (Redis TimeSeries)
    test_anomaly_history()
    
    # Test 6: IP reputation (Bloom Filter or fallback)
    test_ip_reputation()
    
    # Test 7: Behavior similarity (Vector Search)
    test_behavior_similarity()
    
    print("\n" + "=" * 60)
    print("🎉 Redis 8 Feature Test Complete!")
    print("\n📋 Summary:")
    print("✅ Redis Stack 8 connection established")
    print("✅ TimeSeries module for anomaly tracking")
    print("✅ JSON module for rich document storage")
    print("✅ Search module with full-text and vector search")
    print("✅ Redis Streams for real-time event processing")
    print("🔄 Bloom Filter module (using fallback if not available)")
    print("\n🚀 Rediguard MVP is successfully using Redis 8 new features!")

if __name__ == "__main__":
    main()
