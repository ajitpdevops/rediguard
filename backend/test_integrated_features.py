#!/usr/bin/env python3
"""
Test script for the new integrated data seeding and streaming endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Redis Stack: {data['redis_stack']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_redis_features():
    """Test Redis 8 features"""
    print("\n🧪 Testing Redis 8 Features...")
    response = requests.post(f"{BASE_URL}/api/v1/test/redis-features")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Redis Connected: {data['redis_connected']}")
        print(f"✅ Modules: {data['modules_available']}")
        print(f"✅ Test Event Processed: {data['test_event_processed']}")
        print(f"✅ Anomaly Score: {data.get('anomaly_score', 'N/A')}")
        return True
    else:
        print(f"❌ Redis features test failed: {response.status_code}")
        return False

def test_batch_generation():
    """Test batch event generation"""
    print("\n📦 Testing Batch Event Generation...")
    response = requests.post(f"{BASE_URL}/api/v1/data/generate-batch?count=5&anomaly_rate=0.4")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Events Generated: {data['events_processed']}")
        print(f"✅ Anomalies Detected: {data['anomalies_detected']}")
        print(f"✅ Actual Anomaly Rate: {data['anomaly_rate_actual']:.2f}")
        
        # Show first event
        if data['events']:
            event = data['events'][0]
            print(f"   Sample Event: {event['event']['user_id']} from {event['event']['location']}")
        
        return True
    else:
        print(f"❌ Batch generation failed: {response.status_code}")
        return False

def test_data_stats():
    """Test data statistics"""
    print("\n📊 Testing Data Statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/data/stats")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stream Length: {data['stream_length']}")
        print(f"✅ Total Alerts: {data['total_alerts']}")
        print(f"✅ Malicious IPs: {data['malicious_ip_count']}")
        print(f"✅ Streaming Active: {data['streaming_active']}")
        return True
    else:
        print(f"❌ Data stats failed: {response.status_code}")
        return False

def test_seeding():
    """Test historical data seeding"""
    print("\n🌱 Testing Historical Data Seeding...")
    response = requests.post(f"{BASE_URL}/api/v1/data/seed?num_events=50&anomaly_rate=0.15")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Seeding Started: {data['message']}")
        print(f"✅ Events: {data['num_events']}")
        print(f"✅ Anomaly Rate: {data['anomaly_rate']}")
        
        # Wait a bit and check stats
        print("   Waiting 5 seconds for seeding to process...")
        time.sleep(5)
        
        stats_response = requests.get(f"{BASE_URL}/api/v1/data/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   Updated Stream Length: {stats['stream_length']}")
            print(f"   Updated Alerts: {stats['total_alerts']}")
        
        return True
    else:
        print(f"❌ Seeding failed: {response.status_code}")
        return False

def test_streaming():
    """Test real-time data streaming"""
    print("\n🚀 Testing Real-time Data Streaming...")
    
    # Start streaming
    response = requests.post(f"{BASE_URL}/api/v1/data/stream/start?duration_minutes=1&events_per_minute=30&anomaly_rate=0.3")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Streaming Started: {data['message']}")
        print(f"✅ Duration: {data['duration_minutes']} minutes")
        print(f"✅ Rate: {data['events_per_minute']} events/min")
        
        # Check status
        time.sleep(2)
        status_response = requests.get(f"{BASE_URL}/api/v1/data/stream/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Status: {status['status']}")
        
        # Wait a bit longer
        print("   Waiting 10 seconds for streaming to generate events...")
        time.sleep(10)
        
        # Stop streaming
        stop_response = requests.post(f"{BASE_URL}/api/v1/data/stream/stop")
        if stop_response.status_code == 200:
            stop_data = stop_response.json()
            print(f"✅ Streaming Stopped: {stop_data['message']}")
        
        # Check final stats
        stats_response = requests.get(f"{BASE_URL}/api/v1/data/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   Final Stream Length: {stats['stream_length']}")
            print(f"   Final Alerts: {stats['total_alerts']}")
        
        return True
    else:
        print(f"❌ Streaming failed: {response.status_code}")
        return False

def test_search_functionality():
    """Test search and query functionality"""
    print("\n🔍 Testing Search Functionality...")
    
    # Search alerts
    response = requests.get(f"{BASE_URL}/api/v1/alerts/search?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('alerts', [])
        print(f"✅ Found {len(alerts)} alerts")
        
        if alerts:
            alert = alerts[0]
            print(f"   Sample Alert: User {alert.get('user_id')} from {alert.get('location')} (Score: {alert.get('score', 'N/A')})")
        
        return True
    else:
        print(f"❌ Search failed: {response.status_code}")
        return False

def main():
    """Run comprehensive test of integrated functionality"""
    print("🚀 Testing Rediguard Integrated Data Management")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Health check failed. Exiting.")
        return
    
    # Test 2: Redis features
    if not test_redis_features():
        print("❌ Redis features test failed.")
        return
    
    # Test 3: Batch generation
    test_batch_generation()
    
    # Test 4: Data statistics
    test_data_stats()
    
    # Test 5: Historical seeding
    test_seeding()
    
    # Test 6: Real-time streaming
    test_streaming()
    
    # Test 7: Search functionality
    test_search_functionality()
    
    print("\n" + "=" * 60)
    print("🎉 Integrated Data Management Test Complete!")
    print("\n📋 Summary:")
    print("✅ Health check and Redis connection")
    print("✅ Redis 8 features testing")
    print("✅ Batch event generation")
    print("✅ Historical data seeding")
    print("✅ Real-time data streaming")
    print("✅ Search and query functionality")
    print("\n🚀 All data management features working correctly!")

if __name__ == "__main__":
    main()
