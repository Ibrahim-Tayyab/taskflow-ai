"""
Quick test to verify conversation creation works
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
    exit(1)

token = response.json().get("token")
print(f"✅ Login successful!")

headers = {"Authorization": f"Bearer {token}"}

# Create a conversation
print("\n📝 Creating conversation...")
response = requests.post(
    f"{BASE_URL}/api/conversations",
    json={"title": "Hi"},
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    conv = response.json()
    print(f"✅ Created conversation: {conv}")
    
    # List conversations
    print("\n📋 Listing conversations...")
    response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
    convs = response.json()
    print(f"✅ Found {len(convs)} conversations")
    for c in convs:
        print(f"  - [{c['id']}] {c['title']}")
else:
    print(f"❌ Failed: {response.text}")
