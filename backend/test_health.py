#!/usr/bin/env python3
"""
Simple health check script for testing the backend locally
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_health():
    """Test the backend health and basic functionality"""
    
    print("🔍 Testing backend health...")
    
    try:
        # Test imports
        print("Testing imports...")
        from app.models import LoginEvent, HealthCheck, SecurityAlert
        from app.api.routes import router
        from main import app
        print("✅ All imports successful")
        
        # Test basic FastAPI app structure
        print(f"App title: {app.title}")
        print(f"Available routes: {len(app.routes)}")
        
        # Test model creation
        print("Testing model creation...")
        test_event = LoginEvent(
            user_id="test_user",
            ip="192.168.1.100",
            location="Test Location",
            timestamp=int(time.time())
        )
        print(f"✅ Created test event: {test_event.user_id}")
        
        print("✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("REDIS_HOST", "localhost")
    os.environ.setdefault("REDIS_PORT", "6379")
    
    success = asyncio.run(test_health())
    sys.exit(0 if success else 1)
