#!/usr/bin/env python3
"""Simple test script for Rediguard backend API"""

import requests
import json

# Test the API
try:
    # Health check
    response = requests.get("http://localhost:8000/api/v1/health")
    print(f"Health: {response.status_code} - {response.json()}")
    
    # Generate demo events
    response = requests.post("http://localhost:8000/api/v1/demo/generate-events?count=5")
    print(f"Demo events: {response.status_code} - Generated events")
    
    # Add login event
    event = {"user_id": "alice", "ip": "192.168.1.10", "location": "NYC"}
    response = requests.post("http://localhost:8000/api/v1/events/login", json=event)
    print(f"Login event: {response.status_code} - {response.json()}")
    
    # Check stats
    response = requests.get("http://localhost:8000/api/v1/stats/overview")
    print(f"Stats: {response.status_code} - {response.json()}")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
