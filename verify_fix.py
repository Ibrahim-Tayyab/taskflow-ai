import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_signup():
    email = f"test_fix_{int(time.time())}@example.com"
    payload = {
        "email": email,
        "password": "password123",
        "name": "Test Fix User"
    }
    print(f"Testing Signup with {email}...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            return None
    except Exception as e:
        print(f"Signup failed: {e}")
        return None

def test_conversations(token):
    print("\nTesting Conversation History...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        print("Testing /api/conversations (no slash)...")
        response = requests.get(f"{BASE_URL}/api/conversations", headers=headers, allow_redirects=False)
        print(f"Status: {response.status_code}")
        
        print("Testing /api/conversations/ (with slash)...")
        response2 = requests.get(f"{BASE_URL}/api/conversations/", headers=headers, allow_redirects=False)
        print(f"Status (with slash): {response2.status_code}")
        if response2.status_code == 200:
            print("Response (with slash): Success")
            
    except Exception as e:
        print(f"Conversations failed: {e}")

if __name__ == "__main__":
    token = test_signup()
    if token:
        test_conversations(token)
