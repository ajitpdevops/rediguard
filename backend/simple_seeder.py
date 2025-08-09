#!/usr/bin/env python3
"""
Simple Data Seeder for Rediguard - Seeds data via API calls
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict

# Configuration
BASE_URL = "http://localhost:8000"

# Sample data
USERS = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry"]
LOCATIONS = [
    "New York, US", "London, UK", "Tokyo, JP", "Sydney, AU",
    "Berlin, DE", "Toronto, CA", "Mumbai, IN", "São Paulo, BR",
    "Moscow, RU", "Beijing, CN", "Lagos, NG", "Tehran, IR"
]

def generate_login_event(anomalous: bool = False) -> Dict:
    """Generate a login event"""
    user = random.choice(USERS)
    
    if anomalous:
        # Anomalous patterns
        ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        location = random.choice(LOCATIONS[-4:])  # High-risk locations
        # Unusual time (late night/early morning)
        base_time = datetime.now().replace(hour=random.choice([2, 3, 4, 23, 0, 1]))
    else:
        # Normal patterns
        ip = f"192.168.{random.randint(1, 10)}.{random.randint(1, 100)}"
        location = random.choice(LOCATIONS[:6])  # Low-risk locations
        # Normal business hours
        base_time = datetime.now().replace(hour=random.randint(9, 17))
    
    return {
        "user_id": user,
        "ip": ip,
        "location": location,
        "timestamp": int(base_time.timestamp())
    }

def seed_data(num_events: int = 100):
    """Seed data via API"""
    print(f"🌱 Seeding {num_events} events...")
    
    successful = 0
    anomalies = 0
    
    for i in range(num_events):
        # 20% chance of anomalous event
        is_anomalous = random.random() < 0.2
        event = generate_login_event(is_anomalous)
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/events/login", json=event)
            
            if response.status_code == 200:
                successful += 1
                result = response.json()
                
                if result.get("is_anomaly", False):
                    anomalies += 1
                    print(f"🚨 Anomaly detected: {event['user_id']} from {event['location']}")
                
                if (i + 1) % 25 == 0:
                    print(f"   Progress: {i + 1}/{num_events} events processed ({anomalies} anomalies)")
                    
            else:
                print(f"❌ Failed to create event {i}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating event {i}: {e}")
    
    print(f"✅ Seeding complete: {successful}/{num_events} events created, {anomalies} anomalies detected")

def stream_data(duration_minutes: int = 10, events_per_minute: int = 6):
    """Stream data continuously"""
    print(f"🚀 Streaming data for {duration_minutes} minutes at {events_per_minute} events/minute...")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    total_events = 0
    total_anomalies = 0
    
    try:
        while time.time() < end_time:
            # Generate events for this minute
            for _ in range(events_per_minute):
                is_anomalous = random.random() < 0.25  # 25% anomaly rate for streaming
                event = generate_login_event(is_anomalous)
                
                try:
                    response = requests.post(f"{BASE_URL}/api/v1/events/login", json=event)
                    
                    if response.status_code == 200:
                        total_events += 1
                        result = response.json()
                        
                        if result.get("is_anomaly", False):
                            total_anomalies += 1
                            print(f"🚨 LIVE ANOMALY: {event['user_id']} from {event['location']} (Score: {result.get('anomaly_score', 'N/A')})")
                    
                    # Small delay between events
                    time.sleep(60 / events_per_minute)
                    
                except Exception as e:
                    print(f"❌ Stream error: {e}")
            
            elapsed_minutes = (time.time() - start_time) / 60
            print(f"📊 Streaming: {total_events} events in {elapsed_minutes:.1f}m ({total_anomalies} anomalies)")
            
    except KeyboardInterrupt:
        print("🛑 Streaming stopped by user")
    
    total_time = (time.time() - start_time) / 60
    print(f"✅ Streaming complete: {total_events} events in {total_time:.1f} minutes")

def test_endpoints():
    """Test various API endpoints"""
    print("🔍 Testing API endpoints...")
    
    endpoints = [
        ("/health", "GET"),
        ("/api/v1/alerts/search?limit=5", "GET"),
        ("/api/v1/demo/generate-data?num_events=3", "POST"),
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - OK")
                if "health" in endpoint:
                    data = response.json()
                    modules = data.get("redis_modules", {})
                    print(f"   Redis modules: TimeSeries={modules.get('timeseries')}, JSON={modules.get('json')}, Search={modules.get('search')}")
                    
            else:
                print(f"❌ {method} {endpoint} - {response.status_code}")
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")

def main():
    """Main function"""
    print("🚀 Rediguard Data Seeder & Streamer")
    print("=" * 50)
    
    # Test connectivity first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running on localhost:8000")
        return
    
    while True:
        print("\nChoose an option:")
        print("1. Test API endpoints")
        print("2. Seed 50 events")
        print("3. Seed 200 events")
        print("4. Stream for 5 minutes")
        print("5. Stream for 15 minutes")
        print("6. Seed 100 + Stream 10 minutes")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            test_endpoints()
        elif choice == "2":
            seed_data(50)
        elif choice == "3":
            seed_data(200)
        elif choice == "4":
            stream_data(5, 6)
        elif choice == "5":
            stream_data(15, 6)
        elif choice == "6":
            seed_data(100)
            print("\n" + "="*30)
            stream_data(10, 6)
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
