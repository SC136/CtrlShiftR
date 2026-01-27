"""
Final comprehensive test - Real LLM via API
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("🧪 Test 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200 and response.json()["status"] == "ok":
        print("✅ PASS\n")
        return True
    print("❌ FAIL\n")
    return False


def test_real_llm_high_confidence():
    """Test real LLM with high confidence"""
    print("🧪 Test 2: Real LLM - High Confidence (Early Blight)")
    print("=" * 60)
    
    payload = {
        "crop": "Tomato",
        "issue": "Early Blight",
        "confidence": 0.87,
        "season": "Kharif",
        "location": "Maharashtra"
    }
    
    print(f"📤 Sending: {json.dumps(payload, indent=2)}")
    print("⏳ Waiting for LLM response (this may take 5-10 seconds)...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/reason", json=payload, timeout=120)
    elapsed = time.time() - start
    
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📄 Response:")
        print(json.dumps(data, indent=2))
        
        if "problem" in data and "reason" in data:
            print("\n✅ PASS - Real LLM generated farmer advice!\n")
            return True
        elif "message" in data:
            print("\n⚠️  Returned fallback message\n")
            return False
    
    print("❌ FAIL\n")
    return False


def test_low_confidence():
    """Test low confidence fallback"""
    print("🧪 Test 3: Low Confidence (Safety Guardrail)")
    print("=" * 60)
    
    payload = {
        "crop": "Tomato",
        "issue": "Unknown",
        "confidence": 0.45,
        "season": "Kharif",
        "location": "Maharashtra"
    }
    
    print(f"📤 Sending: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/reason", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📄 Response:")
        print(json.dumps(data, indent=2))
        
        if "message" in data and "not clear" in data["message"].lower():
            print("\n✅ PASS - Safety guardrail working!\n")
            return True
    
    print("❌ FAIL\n")
    return False


def test_another_disease():
    """Test with different disease"""
    print("🧪 Test 4: Real LLM - Different Disease (Leaf Curl)")
    print("=" * 60)
    
    payload = {
        "crop": "Tomato",
        "issue": "Leaf Curl",
        "confidence": 0.92,
        "season": "Rabi",
        "location": "Punjab"
    }
    
    print(f"📤 Sending: {json.dumps(payload, indent=2)}")
    print("⏳ Waiting for LLM response...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/reason", json=payload, timeout=120)
    elapsed = time.time() - start
    
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📄 Response:")
        print(json.dumps(data, indent=2))
        
        if "problem" in data:
            print("\n✅ PASS - LLM handled different disease!\n")
            return True
    
    print("❌ FAIL\n")
    return False


if __name__ == "__main__":
    print("🚀 FINAL COMPREHENSIVE API TEST")
    print("=" * 60)
    print("Testing Farmer Assistant with Real Qwen LLM\n")
    
    results = []
    
    try:
        # Test 1: Health
        results.append(("Health Check", test_health()))
        
        # Test 2: Real LLM - High confidence
        results.append(("Real LLM (Early Blight)", test_real_llm_high_confidence()))
        
        # Test 3: Low confidence
        results.append(("Low Confidence Safety", test_low_confidence()))
        
        # Test 4: Different disease
        results.append(("Real LLM (Leaf Curl)", test_another_disease()))
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("Make sure the server is running: uvicorn main:app --reload")
        exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉🎉🎉 ALL TESTS PASSED! 🎉🎉🎉")
        print("✅ Real Qwen LLM is fully integrated!")
        print("✅ FastAPI server is working!")
        print("✅ Safety guardrails are active!")
        print("✅ Farmer-friendly responses generated!")
        print("\n🌾 FARMER ASSISTANT IS READY FOR USE! 🌾")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
