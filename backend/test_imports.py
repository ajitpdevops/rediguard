#!/usr/bin/env python3
"""
Test module imports for CI/CD pipeline
"""

def main():
    print("🔍 Testing backend imports...")
    
    import sys
    import os
    
    # Print debug information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[:5]}...")  # Show first 5 paths
    
    try:
        # Test app.models import
        from app.models import LoginEvent, HealthCheck, SecurityAlert
        print("✅ app.models import successful")
        
        # Test app.api.routes import
        from app.api.routes import router
        print("✅ app.api.routes import successful")
        
        # Test main app import
        from main import app
        print("✅ main app import successful")
        print(f"FastAPI app has {len(app.routes)} routes")
        
        # Test basic model creation
        import time
        test_event = LoginEvent(
            user_id="test_user",
            ip="192.168.1.100",
            location="Test Location",
            timestamp=int(time.time())
        )
        print(f"✅ Created test LoginEvent for user: {test_event.user_id}")
        
        print("✅ All import tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
