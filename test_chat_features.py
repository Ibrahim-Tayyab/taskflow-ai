
import os
import requests
import json
import time

# --- Config ---
BASE_URL = "http://localhost:8000/api/chat/"
# Need to use an existing user? or signup? Default test user.
# Auth token management is tricky.
# We will use the same hardcoded auth approach as previous tests if possible.
# But previous test had signup.
# I'll replicate the signup/login flow from 'test_chat_slash.py' (I need to remember it, or just use a generic user if I can).

# Actually, I'll rely on the backend being open or handle auth properly.
# `test_chat_slash.py` did:
# 1. Signup random
# 2. Login
# 3. Chat

import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_test():
    # 1. Signup/Login
    username = f"testuser_{random_string(5)}"
    email = f"{username}@example.com"
    password = "TestPassword123!"
    
    print(f"Creating user: {email}")
    auth_url = "http://localhost:8000/api/auth"
    
    signup_res = requests.post(f"{auth_url}/signup", json={"email": email, "password": password, "full_name": "Test User"})
    print(f"Signup Status: {signup_res.status_code}")
    # Try Multipart
    login_res = requests.post(f"{auth_url}/login", files={"username": (None, email), "password": (None, password), "grant_type": (None, "password")})
    print(f"Login Status: {login_res.status_code}")
    
    if login_res.status_code != 200:
        try:
            print(f"Login Failed Content: {json.dumps(login_res.json(), indent=2)}")
        except:
             print(f"Login Failed Content (Text): {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Logged in. Token acquired.")

    # 2. Test Typo Handling (Add Task)
    # "add nam itr" -> "Title: itr" using Gemini 2.0 inference
    print("\nTest 1: Typo Handling (Add Task)")
    msg1 = {"messages": [{"role": "user", "content": "add nam itr priority hight"}]}
    res1 = requests.post(BASE_URL, json=msg1, headers=headers)
    print(f"Response: {res1.json()}")
    
    # 3. Test Search
    print("\nTest 2: Search Tasks")
    msg2 = {"messages": [{"role": "user", "content": "search for itr"}]}
    res2 = requests.post(BASE_URL, json=msg2, headers=headers)
    print(f"Response: {res2.json()}")
    
    # 4. Test Analytics
    print("\nTest 3: Analytics")
    msg3 = {"messages": [{"role": "user", "content": "show me analytics"}]}
    res3 = requests.post(BASE_URL, json=msg3, headers=headers)
    print(f"Response: {res3.json()}")

if __name__ == "__main__":
    run_test()
