"""
Quick test script to verify chat history and task operations.
Tests the implementation with the provided credentials.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "ali@gmail.com"
PASSWORD = "ali1Q@gmail.com"

def test_login():
    """Test login and get token"""
    print("\n🔐 Testing Login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_chat_message(token):
    """Test sending a chat message"""
    print("\n💬 Testing Chat Message...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/chat/",
        headers=headers,
        json={
            "messages": [
                {"role": "user", "content": "Add task to buy groceries priority high"}
            ]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat response: {data.get('response')[:100]}...")
        print(f"   Source: {data.get('source')}")
        return True
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(response.text)
        return False

def test_save_message(token):
    """Test saving a message to history"""
    print("\n💾 Testing Save Message...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(
        f"{BASE_URL}/api/chat/save-message",
        headers=headers,
        json={
            "role": "user",
            "content": "Test message for history",
            "source": None
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message saved! ID: {data.get('id')}")
        return True
    else:
        print(f"❌ Save failed: {response.status_code}")
        print(response.text)
        return False

def test_get_history(token):
    """Test retrieving chat history"""
    print("\n📜 Testing Get History...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/chat/history",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved {len(data)} messages")
        if data:
            print(f"   Latest: {data[-1].get('content')[:50]}...")
        return True
    else:
        print(f"❌ Get history failed: {response.status_code}")
        print(response.text)
        return False

def test_list_tasks(token):
    """Test listing tasks"""
    print("\n📋 Testing List Tasks...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/tasks/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} tasks")
        for task in data[:3]:  # Show first 3
            print(f"   - {task.get('description')} (Priority: {task.get('priority')})")
        return True
    else:
        print(f"❌ List tasks failed: {response.status_code}")
        print(response.text)
        return False

def test_clear_history(token):
    """Test clearing chat history"""
    print("\n🗑️  Testing Clear History...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/api/chat/history",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cleared {data.get('count')} messages")
        return True
    else:
        print(f"❌ Clear history failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("=" * 60)
    print("🧪 CHAT HISTORY & TASK MANAGEMENT TEST SUITE")
    print("=" * 60)
    print(f"Testing with account: {EMAIL}")
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without token")
        return
    
    # Run tests
    test_save_message(token)
    test_get_history(token)
    test_chat_message(token)
    test_list_tasks(token)
    
    # Optional: Clear history (commented out to preserve data)
    # test_clear_history(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
