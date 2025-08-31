import requests
import json

def test_ngrok_bypass():
    """Test ngrok bypass with different methods"""
    
    base_url = "https://ffd4cc77368b.ngrok-free.app"
    
    # Test 1: With ngrok-skip-browser-warning header
    print("Testing with ngrok-skip-browser-warning header...")
    try:
        headers = {
            'ngrok-skip-browser-warning': 'true',
            'User-Agent': 'CustomBot/1.0'
        }
        response = requests.get(f"{base_url}/ngrok-bypass", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}...")
        print("✅ Success with bypass header!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: With custom User-Agent only
    print("Testing with custom User-Agent...")
    try:
        headers = {
            'User-Agent': 'NonBrowserApp/2.0 (Custom Application)'
        }
        response = requests.get(f"{base_url}/bypass-ngrok", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}...")
        print("✅ Success with custom User-Agent!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Main page with bypass
    print("Testing main page with bypass...")
    try:
        headers = {
            'ngrok-skip-browser-warning': 'true',
            'User-Agent': 'CustomBot/1.0'
        }
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}...")
        print("✅ Success accessing main page!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ngrok_bypass()
