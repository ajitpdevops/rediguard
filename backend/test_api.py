#!/usr/bin/env python3
"""Test script for Rediguard backend API"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing Rediguard Backend API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
    
    # Test login event ingestion
    try:
        login_event = {
            "user_id": "test_user_001",
            "ip": "192.168.1.100",
            "location": "New York, US"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/events/login",
            json=login_event
        )
        print(f"Login event ingestion: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing login event: {e}")
    
    # Test stats
    try:
        response = requests.get(f"{base_url}/api/v1/stats/overview")
        print(f"Stats endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing stats: {e}")

if __name__ == "__main__":
    test_api()
