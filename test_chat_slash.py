import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_chat():
    email = "tester@example.com"
    password = "password123"
    
    # Login again to be sure (using same email/pass)
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    if response.status_code != 200:
        print(f"Auth failed: {response.text}")
        return

    token = response.json().get("token")
    print(f"Got token: {token[:10]}...")

    # 2. Test Chat WITH TRAILING SLASH
    print("\nSending 'Hi' to chatbot (with slash)...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    
    try:
        chat_res = requests.post(f"{BASE_URL}/chat/", headers=headers, json=payload)
        print(f"Status: {chat_res.status_code}")
        print(f"Response: {chat_res.text}")
    except Exception as e:
        print(f"Chat request failed: {e}")

if __name__ == "__main__":
    test_chat()
