
import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from sqlmodel import Session, select, create_engine
from core.config import settings
from models.conversation import Conversation
from models.chat_message import ChatMessage

def debug_db():
    print(f"🔌 Connecting to DB: {settings.database_url.split('@')[1]}") # Hide credentials
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Check Conversations
        conversations = session.exec(select(Conversation)).all()
        print(f"\n📂 Total Conversations in DB: {len(conversations)}")
        for c in conversations:
            print(f"   - ID: {c.id} | Title: {c.title} | User: {c.user_id}")
            
        # Check Messages
        messages = session.exec(select(ChatMessage)).all()
        print(f"\n💬 Total Messages in DB: {len(messages)}")
        for m in messages[:5]:
             print(f"   - ID: {m.id} | Content: {m.content[:20]}... | ConvID: {m.conversation_id}")
             
        # Check Orphaned Messages
        orphans = [m for m in messages if m.conversation_id is None]
        print(f"\n⚠️ Orphaned Messages (No ConvID): {len(orphans)}")

if __name__ == "__main__":
    try:
        debug_db()
    except Exception as e:
        print(f"❌ Error: {e}")
