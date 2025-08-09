#!/usr/bin/env python3
"""Comprehensive test script for Rediguard backend API"""

import requests
import json
import time
import random

def test_comprehensive_api():
    base_url = "http://localhost:8000"
    
    print("🔒 REDIGUARD BACKEND COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"   ✅ Health Status: {response.status_code}")
        health_data = response.json()
        print(f"   📊 Redis Connected: {health_data['redis_connected']}")
        print(f"   🔧 Features Initialized: {health_data['features_initialized']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Generate Demo Events
    print("\n2️⃣ Generating Demo Events...")
    try:
        response = requests.post(f"{base_url}/api/v1/demo/generate-events?count=20")
        print(f"   ✅ Demo Generation: {response.status_code}")
        demo_data = response.json()
        print(f"   📈 Generated {len(demo_data['events'])} events")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Manual Login Events
    print("\n3️⃣ Testing Manual Login Events...")
    
    # Normal login
    normal_event = {
        "user_id": "alice",
        "ip": "192.168.1.10",
        "location": "New York, US"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/events/login", json=normal_event)
        print(f"   ✅ Normal Login: {response.status_code}")
        print(f"   📋 Stream ID: {response.json().get('stream_id')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Suspicious login (malicious IP)
    suspicious_event = {
        "user_id": "alice",
        "ip": "192.168.1.100",  # This is in our malicious IP set
        "location": "Moscow, RU"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/events/login", json=suspicious_event)
        print(f"   ⚠️  Suspicious Login: {response.status_code}")
        print(f"   📋 Stream ID: {response.json().get('stream_id')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: IP Security Check
    print("\n4️⃣ Testing IP Security Checks...")
    
    # Check normal IP
    try:
        response = requests.get(f"{base_url}/api/v1/security/check-ip/192.168.1.10")
        result = response.json()
        print(f"   ✅ Normal IP (192.168.1.10): Not malicious = {not result['is_malicious']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check malicious IP
    try:
        response = requests.get(f"{base_url}/api/v1/security/check-ip/192.168.1.100")
        result = response.json()
        print(f"   🚨 Malicious IP (192.168.1.100): Is malicious = {result['is_malicious']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Add new malicious IP
    try:
        response = requests.post(f"{base_url}/api/v1/security/add-malicious-ip?ip=10.0.0.100")
        print(f"   ➕ Added New Malicious IP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: AI Analysis
    print("\n5️⃣ Testing AI Analysis...")
    
    test_event = {
        "user_id": "bob",
        "ip": "203.0.113.50",
        "location": "Singapore",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/ai/analyze-event", json=test_event)
        analysis = response.json()
        print(f"   🤖 AI Analysis: {response.status_code}")
        print(f"   📊 Anomaly Score: {analysis.get('anomaly_score', 'N/A'):.3f}")
        print(f"   🧠 Feature Count: {len(analysis.get('features', []))}")
        print(f"   🔍 Similar Behaviors Found: {len(analysis.get('similar_behaviors', []))}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Wait a moment for processing
    print("\n⏳ Waiting for event processing...")
    time.sleep(2)
    
    # Test 6: Search Alerts
    print("\n6️⃣ Searching Security Alerts...")
    
    # Search high-score alerts
    try:
        response = requests.get(f"{base_url}/api/v1/alerts/search?min_score=0.7&limit=10")
        alerts = response.json()
        print(f"   🔍 High-Score Alerts: {response.status_code}")
        print(f"   🚨 Found {alerts['total']} high-risk alerts")
        
        for alert in alerts['alerts'][:3]:  # Show first 3
            print(f"      - User: {alert['user_id']}, Score: {alert['score']:.3f}, IP: {alert['ip']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Search recent alerts
    try:
        recent_time = int(time.time()) - 3600  # Last hour
        response = requests.get(f"{base_url}/api/v1/alerts/search?start_time={recent_time}")
        alerts = response.json()
        print(f"   ⏰ Recent Alerts (1h): Found {alerts['total']} alerts")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: User Anomaly History
    print("\n7️⃣ Getting User Anomaly History...")
    try:
        response = requests.get(f"{base_url}/api/v1/users/alice/anomaly-history?hours=24")
        history = response.json()
        print(f"   📈 Alice's Anomaly History: {response.status_code}")
        print(f"   📊 Data Points: {len(history)}")
        
        if history:
            avg_score = sum(point['score'] for point in history) / len(history)
            print(f"   📉 Average Score: {avg_score:.3f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 8: System Stats
    print("\n8️⃣ Getting System Statistics...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats/overview")
        stats = response.json()
        print(f"   📊 System Stats: {response.status_code}")
        print(f"   📋 Events in Stream: {stats.get('stream_length', 0)}")
        print(f"   🚨 Total Alerts: {stats.get('total_alerts', 0)}")
        print(f"   🔒 Malicious IPs: {stats.get('malicious_ip_count', 0)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 REDIGUARD BACKEND TEST COMPLETED!")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("📊 RedisInsight: http://localhost:8001")

if __name__ == "__main__":
    test_comprehensive_api()
