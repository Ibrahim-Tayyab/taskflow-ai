import os
from dotenv import load_dotenv

# Load env from api/.env
env_path = os.path.join(os.path.dirname(__file__), 'api', '.env')
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

or_key = os.getenv("OPENROUTER_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

print(f"OPENROUTER_API_KEY found: {'Yes' if or_key else 'No'}")
if or_key:
    print(f"OPENROUTER_API_KEY length: {len(or_key)}")
    print(f"OPENROUTER_API_KEY start: {or_key[:5]}...")

print(f"GOOGLE_API_KEY found: {'Yes' if google_key else 'No'}")
if google_key:
    print(f"GOOGLE_API_KEY length: {len(google_key)}")
    print(f"GOOGLE_API_KEY start: {google_key[:5]}...")
