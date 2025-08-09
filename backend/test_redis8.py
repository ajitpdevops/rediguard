#!/usr/bin/env python3
"""Test Redis Stack 8 features"""

import redis
import time
import json
import numpy as np
from datetime import datetime

def test_redis_8_features():
    """Test Redis 8 new data types and features"""
    print("🔍 Testing Redis 8 Features...")
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=False)
        r.ping()
        print("✅ Connected to Redis")
        
        # Check Redis version
        info = r.info()
        redis_version = info.get('redis_version', 'unknown')
        print(f"📊 Redis Version: {redis_version}")
        
        # Check loaded modules
        print("\n🔧 Checking Redis Modules:")
        try:
            modules = r.execute_command("MODULE", "LIST")
            for module_info in modules:
                if isinstance(module_info, list) and len(module_info) >= 2:
                    module_name = module_info[1].decode() if isinstance(module_info[1], bytes) else module_info[1]
                    print(f"  - {module_name}")
        except Exception as e:
            print(f"  ❌ Could not check modules: {e}")
        
        print("\n🧪 Testing Redis 8 Data Types:")
        
        # Test 1: Redis Streams
        print("\n1️⃣ Testing Redis Streams:")
        try:
            stream_id = r.xadd("test:stream", {
                "user": "alice",
                "action": "login", 
                "timestamp": str(int(time.time()))
            })
            print(f"  ✅ Added to stream: {stream_id}")
            
            # Read from stream
            messages = r.xread({"test:stream": "0"}, count=1)
            print(f"  ✅ Read from stream: {len(messages[0][1]) if messages else 0} messages")
        except Exception as e:
            print(f"  ❌ Streams error: {e}")
        
        # Test 2: Redis TimeSeries (if available)
        print("\n2️⃣ Testing Redis TimeSeries:")
        try:
            # Try to create a time series
            r.execute_command("TS.CREATE", "test:ts", "RETENTION", 3600000)
            
            # Add data points
            timestamp = int(time.time() * 1000)
            r.execute_command("TS.ADD", "test:ts", timestamp, 42.5)
            r.execute_command("TS.ADD", "test:ts", timestamp + 1000, 43.2)
            
            # Query time series
            result = r.execute_command("TS.RANGE", "test:ts", timestamp, timestamp + 2000)
            print(f"  ✅ TimeSeries working: {len(result)} data points")
            
        except Exception as e:
            print(f"  ❌ TimeSeries error: {e}")
        
        # Test 3: Redis JSON (if available)
        print("\n3️⃣ Testing Redis JSON:")
        try:
            test_json = {
                "user": "bob",
                "score": 85.5,
                "tags": ["security", "analysis"],
                "metadata": {"created": datetime.now().isoformat()}
            }
            
            # Set JSON document
            r.execute_command("JSON.SET", "test:json", "$", json.dumps(test_json))
            
            # Get JSON document
            result = r.execute_command("JSON.GET", "test:json")
            parsed = json.loads(result.decode() if isinstance(result, bytes) else result)
            print(f"  ✅ JSON working: user={parsed['user']}, score={parsed['score']}")
            
        except Exception as e:
            print(f"  ❌ JSON error: {e}")
        
        # Test 4: Redis Bloom Filter (if available)
        print("\n4️⃣ Testing Redis Bloom Filter:")
        try:
            # Create bloom filter
            r.execute_command("BF.RESERVE", "test:bloom", 0.01, 1000)
            
            # Add items
            r.execute_command("BF.ADD", "test:bloom", "malicious_ip_1")
            r.execute_command("BF.ADD", "test:bloom", "malicious_ip_2")
            
            # Check existence
            exists1 = r.execute_command("BF.EXISTS", "test:bloom", "malicious_ip_1")
            exists2 = r.execute_command("BF.EXISTS", "test:bloom", "safe_ip")
            
            print(f"  ✅ Bloom Filter working: malicious_ip_1={bool(exists1)}, safe_ip={bool(exists2)}")
            
        except Exception as e:
            print(f"  ❌ Bloom Filter error: {e}")
        
        # Test 5: Redis Search (if available)
        print("\n5️⃣ Testing Redis Search:")
        try:
            # Create search index
            r.execute_command(
                "FT.CREATE", "test:idx", 
                "ON", "JSON",
                "PREFIX", "1", "doc:",
                "SCHEMA", 
                "$.title", "AS", "title", "TEXT",
                "$.score", "AS", "score", "NUMERIC"
            )
            
            # Add searchable document
            doc = {"title": "Security Alert", "score": 95.5, "category": "threat"}
            r.execute_command("JSON.SET", "doc:1", "$", json.dumps(doc))
            
            # Search
            time.sleep(0.1)  # Give time for indexing
            search_result = r.execute_command("FT.SEARCH", "test:idx", "Security")
            print(f"  ✅ Search working: found {search_result[0] if search_result else 0} documents")
            
        except Exception as e:
            print(f"  ❌ Search error: {e}")
        
        # Test 6: Vector Search (if available)
        print("\n6️⃣ Testing Vector Search:")
        try:
            # Create vector index
            r.execute_command(
                "FT.CREATE", "test:vector_idx",
                "ON", "HASH",
                "PREFIX", "1", "vec:",
                "SCHEMA",
                "embedding", "VECTOR", "HNSW", "6",
                "TYPE", "FLOAT32",
                "DIM", "4",
                "DISTANCE_METRIC", "COSINE"
            )
            
            # Add vector
            vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
            r.hset("vec:1", mapping={"embedding": vector.tobytes()})
            
            # Search for similar vectors
            query_vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
            search_result = r.execute_command(
                "FT.SEARCH", "test:vector_idx",
                "*=>[KNN 1 @embedding $query_vector AS distance]",
                "PARAMS", "2", "query_vector", query_vector.tobytes(),
                "DIALECT", "2"
            )
            print(f"  ✅ Vector Search working: found {search_result[0] if search_result else 0} vectors")
            
        except Exception as e:
            print(f"  ❌ Vector Search error: {e}")
        
        print("\n🎉 Redis 8 Feature Testing Complete!")
        print("🔗 RedisInsight available at: http://localhost:8001")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_redis_8_features()
