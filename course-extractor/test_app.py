#!/usr/bin/env python3
"""
Simple test script for Course Extractor application
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running.")
        return False

def test_extraction_endpoint():
    """Test the course extraction endpoint with a sample URL"""
    # Test with a simple educational website
    test_url = "https://www.coursera.org/courses"
    
    try:
        payload = {
            "urls": [test_url]
        }
        
        print(f"🔄 Testing extraction with: {test_url}")
        response = requests.post(
            'http://localhost:5000/api/extract',
            json=payload,
            timeout=60  # Longer timeout for web scraping
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extraction successful!")
            print(f"   Total courses found: {data.get('total_courses', 0)}")
            print(f"   Results count: {len(data.get('results', []))}")
            
            # Show first few courses if any
            for i, result in enumerate(data.get('results', [])[:2]):
                if result.get('success') and result.get('courses'):
                    print(f"   Sample course {i+1}: {result['courses'][0].get('course_name', 'N/A')}")
            
            return True
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_main_page():
    """Test if the main page loads correctly"""
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            return True
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not load main page: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Course Extractor Tests...")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Main Page", test_main_page),
        ("Health Endpoint", test_health_endpoint),
        ("Extraction Endpoint", test_extraction_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
