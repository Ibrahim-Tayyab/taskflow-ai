"""
Quick script to test chat history API
"""
import requests

BASE_URL = "http://localhost:8000"

# Login
print("🔐 Logging in...")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "ali@gmail.com",
    "password": "ali1Q@gmail.com"
})

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json().get("token")
print(f"✅ Login successful!")

# Get chat history
print("\n📜 Getting chat history...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/chat/history", headers=headers)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Found {len(data)} messages")
    for msg in data[:5]:
        print(f"  - [{msg['role']}]: {msg['content'][:50]}...")
else:
    print(f"❌ Failed: {response.text}")
