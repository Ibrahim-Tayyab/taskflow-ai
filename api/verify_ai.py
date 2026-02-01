
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# Load env from parent directory (since we run from api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(current_dir, ".env") # Try api/.env first

print(f"Loading env from {env_path}")
load_dotenv(env_path)

def test_google():
    print("\n--- Testing Google Gemini ---")
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("❌ GOOGLE_API_KEY not found in env")
        return
    
    print(f"Key found: {key[:5]}...{key[-5:]}")
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, can you hear me?")
        print(f"✅ Google Success! Response: {response.text}")
    except Exception as e:
        print(f"❌ Google Failed: {e}")

def test_openrouter():
    print("\n--- Testing OpenRouter ---")
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("❌ OPENROUTER_API_KEY not found in env")
        return

    print(f"Key found: {key[:5]}...{key[-5:]}")
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": "Hello"}],
        )
        print(f"✅ OpenRouter Success! Response: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenRouter Failed: {e}")

if __name__ == "__main__":
    test_google()
    test_openrouter()
