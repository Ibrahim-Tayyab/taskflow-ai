
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test():
    print("🚀 Starting Persistence Test")
    
    # 1. Login
    print("\n🔐 Logging in...")
    auth_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "ali@gmail.com", 
        "password": "ali1Q@gmail.com"
    })
    
    if auth_res.status_code != 200:
        print(f"❌ Login Failed: {auth_res.text}")
        return
        
    token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login Successful")
    
    # 2. Create Conversation
    print("\n📝 Creating Conversation...")
    # NOTE: Using /api/conversations/ WITH SLASH based on fix
    conv_res = requests.post(
        f"{BASE_URL}/api/conversations/", 
        json={"title": "Persistence Test Chat"},
        headers=headers
    )
    
    if conv_res.status_code != 200:
        print(f"❌ Create Conversation Failed: {conv_res.status_code} {conv_res.text}")
        # Try without slash just in case
        print("   Retrying without slash...")
        conv_res = requests.post(
            f"{BASE_URL}/api/conversations", 
            json={"title": "Persistence Test Chat"},
            headers=headers
        )
        if conv_res.status_code != 200:
             return

    conv_data = conv_res.json()
    conv_id = conv_data["id"]
    print(f"✅ Created Conversation ID: {conv_id}")
    
    # 3. Save Message Linked to Conversation
    print(f"\n💾 Saving Message to Conversation {conv_id}...")
    msg_data = {
        "role": "user",
        "content": "This is a persistent message",
        "conversation_id": conv_id
    }
    
    save_res = requests.post(
        f"{BASE_URL}/api/chat/save-message",
        json=msg_data,
        headers=headers
    )
    
    if save_res.status_code != 200:
        print(f"❌ Save Message Failed: {save_res.text}")
        return
        
    saved_msg = save_res.json()
    print(f"✅ Message Saved. ID: {saved_msg['id']}, Conversation ID: {saved_msg.get('conversation_id')}")
    
    if saved_msg.get('conversation_id') != conv_id:
        print(f"⚠️ WARNING: Returned conversation_id {saved_msg.get('conversation_id')} does not match sent {conv_id}!")
    
    # 4. Fetch History
    print(f"\n📜 Fetching History for Conversation {conv_id}...")
    hist_res = requests.get(
        f"{BASE_URL}/api/chat/history?conversation_id={conv_id}&limit=50",
        headers=headers
    )
    
    if hist_res.status_code != 200:
         print(f"❌ Fetch History Failed: {hist_res.text}")
         return
         
    history = hist_res.json()
    print(f"✅ History Fetched. Count: {len(history)}")
    
    found = False
    for msg in history:
        print(f"   - [{msg['role']}] {msg['content']} (ConvID: {msg.get('conversation_id')})")
        if msg['content'] == "This is a persistent message":
            found = True
            
    if found:
        print("\n🎉 SUCCESS! Message persisted and retrieved correctly.")
    else:
        print("\n❌ FAILURE! Message not found in history.")

if __name__ == "__main__":
    run_test()
