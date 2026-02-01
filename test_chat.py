import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_chat():
    email = "tester@example.com"
    password = "password123"
    
    # 1. Signup (or Login if exists)
    print(f"Authenticating as {email}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": email,
            "password": password,
            "name": "Tester"
        })
        if response.status_code == 400: # Already exists?
            print("User exists, logging in...")
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

    # 2. Test Chat
    print("\nSending 'Hi' to chatbot...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    
    try:
        chat_res = requests.post(f"{BASE_URL}/chat", headers=headers, json=payload)
        print(f"Status: {chat_res.status_code}")
        print(f"Response: {chat_res.text}")
    except Exception as e:
        print(f"Chat request failed: {e}")

if __name__ == "__main__":
    test_chat()
