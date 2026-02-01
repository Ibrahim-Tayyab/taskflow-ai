from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlmodel import Session
import os
import json
from openai import OpenAI
import google.generativeai as genai

from database.session import get_session
from models.task import TaskCreate, TaskUpdate
from models.chat_message import ChatMessageCreate, ChatMessageRead
from services.task_service import TaskService
from services.chat_service import ChatService
from repositories.task_repository import TaskRepository
from repositories.chat_repository import ChatRepository
from core.security import get_current_user_id

router = APIRouter()

# --- Configuration ---
# ========================================
# DUAL-MODEL FALLBACK SYSTEM
# ========================================
# This system provides automatic failover between two AI providers:
#
# PRIMARY MODEL: openai/gpt-4o-mini (via OpenRouter)
#   - Best quality for tool calling and task operations
#   - Tried first in normal operation
#
# BACKUP MODEL: gemini-2.5-flash (via Google Gemini SDK)
#   - Stable, unlimited free tier (1,000 requests/day)
#   - Automatically used if primary fails
#
# FORCE_USE_BACKUP Switch:
#   - Set FORCE_USE_BACKUP=True in .env to bypass OpenRouter and test Gemini directly
#   - Default: False (use Primary first for best quality)
#   - Useful for testing Gemini or when OpenRouter has issues
# ========================================

PRIMARY_MODEL = "openai/gpt-4o-mini"     # Best for tool calling
GEMINI_MODEL = "gemini-2.5-flash"        # Stable Google model

# Force Gemini Mode (defaults to False for production stability)
FORCE_USE_BACKUP = os.getenv("FORCE_USE_BACKUP", "False").lower() == "true"

# --- Models ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str
    source: str # "OpenRouter"

# --- Tools Definition ---
# (Tools list is unchanged, assuming it's above or I should preserve it)
# Since replace_file_content replaces the whole chunk, we need to be careful.
# I will target specific blocks to avoid re-writing 200 lines of tools.

# Block 1: Imports and Config
# Block 2: AI Provider (call_openrouter only)
# Block 3: Main Endpoint (no fallback)

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str
    source: str # "OpenRouter" or "Google"

# --- Tools Definition ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the user's todo list. You must infer title/priority from typos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (fix typos)"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "category": {"type": "string", "description": "Category (e.g. 'work', 'personal') inferred from context"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List existing tasks, optionally filtered by status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Complete a task by ID or by name/title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID number"},
                    "task_name": {"type": "string", "description": "Task title/name"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by ID or by name/title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID number"},
                    "task_name": {"type": "string", "description": "Task title/name"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by keyword (title/description/category).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_analytics",
            "description": "Get statistics about tasks (counts, priority breakdown).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_completed",
            "description": "Delete all completed tasks.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's properties (title, priority, category) by ID or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID number"},
                    "task_name": {"type": "string", "description": "Task title/name to search for"},
                    "new_title": {"type": "string", "description": "New task title/description"},
                    "new_priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority level"},
                    "new_category": {"type": "string", "description": "New category"}
                }
            }
        }
    }
]

# --- Helper Functions ---
def get_task_service():
    repository = TaskRepository()
    return TaskService(repository)

def get_chat_service():
    repository = ChatRepository()
    return ChatService(repository)

def execute_tool(tool_name: str, args: Dict, session: Session, user_id: str, task_service: TaskService):
    try:
        if tool_name == "add_task":
            title = args["title"]
            priority = args.get("priority", "medium")
            category = args.get("category", "General")
            # Enforce lowercase priority for consistency
            priority = priority.lower() if priority else "medium"
            # CRITICAL: Task model uses 'description' field for task name/title
            task_data = TaskCreate(description=title, priority=priority, category=category)
            new_task = task_service.create_task(session, task_data, user_id)
            return f"✅ Task Added Successfully!\nTitle: {new_task.description}\nCategory: {new_task.category}\nPriority: {new_task.priority.upper()}\nID: {new_task.id}"

        elif tool_name == "list_tasks":
            tasks = task_service.get_all_tasks(session, user_id)
            result = []
            status_filter = args.get("status", "all")
            for t in tasks:
                if status_filter == "pending" and t.completed: continue
                if status_filter == "completed" and not t.completed: continue
                status_icon = "✅" if t.completed else "⏳"
                priority_display = t.priority.upper() if t.priority else "MEDIUM"
                result.append(f"{status_icon} **{t.description}**\n   ID: {t.id} | Priority: {priority_display} | Category: {t.category or 'General'}")
            
            if not result:
                return "📋 No tasks found."
            
            header = f"📋 **Your Tasks** ({len(result)} total):\n" + "="*40 + "\n"
            return header + "\n\n".join(result)

        elif tool_name == "complete_task":
            # Support both task_id and task_name
            t_id = args.get("task_id")
            task_name = args.get("task_name")
            
            if not t_id and task_name:
                # Search for task by name
                results = task_service.search_tasks(session, task_name, user_id)
                if results:
                    # Use the first match
                    t_id = results[0].id
                else:
                    return f"❌ No task found with name '{task_name}'. Try listing your tasks first."
            
            if t_id:
                t_id = int(t_id)
                updated = task_service.complete_task(session, t_id, user_id, True)
                if updated:
                    return f"✅ **Task Completed!** (ID: {t_id})\nGreat job! Keep it up! 🎉"
                return f"❌ Task {t_id} not found. Please check the task ID."
            
            return "❌ Please provide either task_id or task_name to complete a task."

        elif tool_name == "delete_task":
            # Support both task_id and task_name
            t_id = args.get("task_id")
            task_name = args.get("task_name")
            
            if not t_id and task_name:
                # Search for task by name
                results = task_service.search_tasks(session, task_name, user_id)
                if results:
                    # Use the first match
                    t_id = results[0].id
                else:
                    return f"❌ No task found with name '{task_name}'. Try listing your tasks first."
            
            if t_id:
                t_id = int(t_id)
                deleted = task_service.delete_task(session, t_id, user_id)
                if deleted:
                    return f"🗑️ **Task Deleted** (ID: {t_id})\nTask removed from your list."
                return f"❌ Task {t_id} not found. Please check the task ID."
            
            return "❌ Please provide either task_id or task_name to delete a task."

        elif tool_name == "search_tasks":
            query = args["query"]
            results = task_service.search_tasks(session, query, user_id)
            if not results:
                return f"🔍 No tasks found matching '{query}'"
            
            task_list = []
            for t in results:
                status_icon = "✅" if t.completed else "⏳"
                task_list.append(f"{status_icon} **{t.description}** (ID: {t.id})")
            
            header = f"🔍 **Search Results for '{query}'** ({len(results)} found):\n" + "="*40 + "\n"
            return header + "\n".join(task_list)

        elif tool_name == "get_task_analytics":
            stats = task_service.get_task_analytics(session, user_id)
            total = stats.get('total_tasks', 0)
            completed = stats.get('completed_tasks', 0)
            pending = stats.get('pending_tasks', 0)
            by_priority = stats.get('tasks_by_priority', {})
            
            response = f"""📊 **Task Analytics**
========================================
📋 Total Tasks: {total}
✅ Completed: {completed}
⏳ Pending: {pending}

**By Priority:**
🔴 High: {by_priority.get('high', 0)}
🟡 Medium: {by_priority.get('medium', 0)}
🟢 Low: {by_priority.get('low', 0)}
"""
            return response

        elif tool_name == "clear_completed":
            count = task_service.clear_completed_tasks(session, user_id)
            if count > 0:
                return f"🗑️ **Cleared!** Removed {count} completed task{'s' if count != 1 else ''}.\nYour list is now cleaner! ✨"
            return "✨ No completed tasks to clear. Your list is already clean!"
        
        elif tool_name == "update_task":
            # Support both task_id and task_name
            t_id = args.get("task_id")
            task_name = args.get("task_name")
            
            if not t_id and task_name:
                # Search for task by name
                results = task_service.search_tasks(session, task_name, user_id)
                if results:
                    t_id = results[0].id
                else:
                    return f"❌ No task found with name '{task_name}'. Try listing your tasks first."
            
            if t_id:
                t_id = int(t_id)
                # Build update data
                update_data = {}
                if args.get("new_title"):
                    update_data["description"] = args["new_title"]
                if args.get("new_priority"):
                    update_data["priority"] = args["new_priority"].lower()
                if args.get("new_category"):
                    update_data["category"] = args["new_category"]
                
                if not update_data:
                    return "❌ Please provide at least one field to update (title, priority, or category)."
                
                # Create TaskUpdate object
                task_update = TaskUpdate(**update_data)
                updated = task_service.update_task(session, t_id, user_id, task_update)
                
                if updated:
                    changes = ", ".join([f"{k.replace('description', 'title')}: {v}" for k, v in update_data.items()])
                    return f"✅ **Task Updated!** (ID: {t_id})\nChanges: {changes}\nTask successfully modified! 🎉"
                return f"❌ Task {t_id} not found. Please check the task ID."
            
            return "❌ Please provide either task_id or task_name to update a task."
            
        return "Unknown tool"
    except Exception as e:
        return f"Tool Error: {str(e)}"

# --- AI Providers ---

# --- AI Providers ---

def call_openrouter(messages, tools):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key: raise Exception("No OpenRouter Key")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://todo-hackathon-app.vercel.app",
            "X-Title": "Todo AI Hackathon",
        }
    )
    
    # Try models in order until one works
    last_error = None
    for model in OPENROUTER_MODELS:
        try:
            print(f"Trying OpenRouter model: {model}")
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            return completion, model
        except Exception as e:
            print(f"OpenRouter Model {model} failed: {e}")
            last_error = e
            continue
    raise last_error or Exception("All OpenRouter models failed")

class MockToolCall:
    def __init__(self, name, args):
        self.id = "call_" + os.urandom(4).hex()
        self.function = type('obj', (object,), {'name': name, 'arguments': json.dumps(args)})
        self.type = 'function'

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockCompletion:
    def __init__(self, message):
        self.choices = [MockChoice(message)]

import time

def call_google_direct(messages, tools, system_instruction):
    """
    Fallback method using official Google Gemini SDK.
    Mimics OpenAI response structure for compatibility.
    Includes persistent retries for Rate Limits.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: raise Exception("No Google API Key found.")

    genai.configure(api_key=api_key)
    
    # Enhanced Tool Instruction for Gemini
    tool_instruction = """
    IMPORTANT: You have access to tools. To use them, output ONLY a JSON object with this format:
    { "tool": "tool_name", "args": { ... } }
    
    Examples:
    - Add Task: { "tool": "add_task", "args": { "title": "Buy Milk", "priority": "high", "category": "Personal" } }
    - Delete Task: { "tool": "delete_task", "args": { "task_name": "Buy Milk" } }
    - List Tasks: { "tool": "list_tasks", "args": { "status": "all" } }
    
    Do not explain. Just output the JSON if an action is needed. Otherwise, reply normally.
    """
    full_system_instruction = system_instruction + "\n" + tool_instruction
    
    last_exception = None
    
    # Retry Loop (3 attempts)
    for attempt in range(3):
        try:
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,  # Use configured Gemini model
                system_instruction=full_system_instruction
            )
            
            gemini_history = []
            for m in messages:
                role = "user" if m['role'] == "user" else "model"
                if m['role'] == "system": continue 
                if m['role'] == "tool" or m['role'] == "function": continue 
                gemini_history.append({"role": role, "parts": [str(m['content'])]})

            last_msg = gemini_history.pop() if gemini_history else None
            if not last_msg: return MockCompletion(MockMessage("Error: No messages")), "Google"

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(last_msg['parts'][0])
            text = response.text
            
            # JSON Parsing logic
            tool_calls = None
            clean_text = text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "").replace("```", "").strip()
            
            if clean_text.startswith("{") and "tool" in clean_text:
                try:
                    data = json.loads(clean_text)
                    if "tool" in data and "args" in data:
                        tool_calls = [MockToolCall(data["tool"], data["args"])]
                        text = None 
                except:
                    pass 
            
            return MockCompletion(MockMessage(text, tool_calls)), "Google (Direct)"
            
        except Exception as e:
            print(f"Google API Attempt {attempt+1} Failed: {e}")
            last_exception = e
            # Wait 5 seconds before retrying (simple backoff for 429s)
            time.sleep(5)
            
    raise last_exception

# --- Main Endpoint ---

@router.post("/", response_model=ChatResponse)
@router.post("", response_model=ChatResponse, include_in_schema=False)
def chat_with_ai(
    request: ChatRequest,
    session: Session = Depends(get_session),
    task_service: TaskService = Depends(get_task_service),
    user_id: str = Depends(get_current_user_id)
):
    # Enhanced Multilingual System Prompt
    system_prompt_text = f"""You are an intelligent, multilingual Todo Assistant for User ID: {user_id}.

🎯 YOUR MISSION: Manage tasks efficiently in ANY language (English, Urdu, Roman Urdu).

✅ LANGUAGE SUPPORT:
- English: "add meeting", "complete task", "show my tasks"
- Roman Urdu: "meeting add karo", "task complete kar do", "sare tasks dikhao"
- Urdu: Support Urdu script if user types in Urdu
- Be flexible with language mixing: "add karo buy milk priority high"

📝 TASK OPERATIONS:
1. ADD TASK: Extract title, category, priority from natural language
   - **SMART DEFAULTS - ALWAYS INFER IF NOT SPECIFIED:**
   
   **Category Rules (choose the best match):**
   - Work keywords (meeting, project, deadline, email, report) → "Work"
   - Shopping keywords (buy, purchase, grocery, milk) → "Shopping"
   - Study keywords (study, learn, homework, exam) → "Study"
   - Health keywords (exercise, gym, doctor) → "Health"
   - Personal keywords (call, birthday, family) → "Personal"
   - Home keywords (clean, repair, laundry) → "Home"
   - Default → "General"
   
   **Priority Rules:**
   - Urgent words (urgent, asap, today, now) → "high"
   - Important words (important, deadline, meeting) → "high"
   - Casual words (maybe, sometime) → "low"
   - Default → "medium"
   
   - "add meeting" → Title="Meeting", Category="Work", Priority="high"
   - "buy milk" → Title="Buy milk", Category="Shopping", Priority="medium"
   - Always fix typos: "mlik"→"Milk", "hight"→"High"

2. LIST TASKS: Show all tasks in formatted way
   - "show tasks", "list tasks", "sare tasks dikhao", "task dikhao"
   - Always use list_tasks tool and format output professionally

3. COMPLETE TASK: Accept task name OR task ID
   - "complete meeting" → Search for task with "meeting" in title
   - "complete task 5" → Complete task ID 5
   - "meeting complete kar do" → Complete task named "meeting"

4. DELETE TASK: Accept task name OR task ID
   - "delete milk" → Search and delete task with "milk" in title
   - "milk delete karo" → Delete task named "milk"

5. SEARCH: Find tasks by keyword
   - "find work tasks", "shopping tasks dikhao"

6. ANALYTICS: Show statistics
   - "how many tasks", "stats dikhao", "kitne tasks hain"

🎨 RESPONSE STYLE:
- Always be professional, clear, and friendly
- Use emojis for visual appeal (✅, 📋, 🎉, etc.)
- Format lists with proper headings
- Show task details clearly (Title, ID, Priority, Category)
- Celebrate completions with encouraging messages

⚡ CRITICAL RULES:
- NEVER say you can't understand - always try to infer intent
- Accept typos and fix them silently
- Support task names in any language
- Always show what you understood and what action you took
- When listing tasks, show ALL details in a clean format
"""

    system_message = {
        "role": "system",
        "content": system_prompt_text
    }
    messages = [system_message] + [{"role": m.role, "content": m.content} for m in request.messages]
    
    try:
        # ========================================
        # CHECK FORCE GEMINI MODE
        # ========================================
        if FORCE_USE_BACKUP:
            print(f"🔄 PURE GEMINI MODE: Using {GEMINI_MODEL} directly (bypassing OpenRouter)")
            # Skip to Gemini directly
            response, model_used = call_google_direct(messages, None, system_prompt_text)
            response_message = response.choices[0].message
            
            # Tool Handling for Gemini
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                func_name = tool_call.function.name
                args = tool_call.function.arguments
                if isinstance(args, str): args = json.loads(args)
                
                print(f"\n🤖 GEMINI TOOL CALLED: {func_name}")
                result = execute_tool(func_name, args, session, user_id, task_service)
                
                # Get final response from Gemini
                final_sys = system_prompt_text + f"\n\nSystem Update: executed {func_name} with result: {result}. Briefly confirm using emojis."
                final_res, _ = call_google_direct(messages, None, final_sys)
                
                # Ensure we have valid content
                response_content = final_res.choices[0].message.content
                if not response_content:
                    response_content = result  # Use tool result directly if Gemini returns None
                
                return ChatResponse(response=response_content, source=f"Gemini ({GEMINI_MODEL})")
            
            # No tool call - direct response
            response_content = response_message.content or "✅ Done!"
            return ChatResponse(response=response_content, source=f"Gemini ({GEMINI_MODEL})")
        
        # ========================================
        # TRY PRIMARY MODEL (GPT-4o-mini)
        # ========================================openai/gpt-4o-mini
        try:
            print(f"🤖 Using Primary Model: {PRIMARY_MODEL}")
            
            # Call OpenRouter with PRIMARY_MODEL
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                default_headers={
                    "HTTP-Referer": "https://todo-hackathon-app.vercel.app",
                    "X-Title": "Todo AI Hackathon",
                }
            )
            
            response = client.chat.completions.create(
                model=PRIMARY_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            
            # Tool Handling (OpenAI Style)
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 Tool Called: {func_name}")
                result = execute_tool(func_name, args, session, user_id, task_service)
                
                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
                
                final_res = client.chat.completions.create(
                    model=PRIMARY_MODEL,
                    messages=messages
                )
                return ChatResponse(response=final_res.choices[0].message.content, source=f"Primary ({PRIMARY_MODEL})")
                
            content = response_message.content
            if not content: content = "✅ Done!"
            return ChatResponse(response=content, source=f"Primary ({PRIMARY_MODEL})")

        except Exception as primary_error:
            # ========================================
            # AUTOMATIC FALLBACK TO GEMINI
            # ========================================
            print(f"⚠️ Primary Model Failed: {primary_error}")
            print(f"🔄 AUTOMATIC FALLBACK: Switching to Gemini ({GEMINI_MODEL})...")
            
            # Use Google Gemini 2.5 Flash (Direct SDK)
            response, model_used = call_google_direct(messages, None, system_prompt_text)
            response_message = response.choices[0].message
            
            # Tool Handling (Mock Style for Gemini)
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                func_name = tool_call.function.name
                # args are already dict in MockToolCall, but let's be safe if it's string
                args = tool_call.function.arguments
                if isinstance(args, str): args = json.loads(args)
                
                result = execute_tool(func_name, args, session, user_id, task_service)
                
                # Summarize result with Google
                final_sys = system_prompt_text + f"\n\nSystem Update: executed {func_name} with result: {result}. Briefly confirm using emojis."
                final_res, _ = call_google_direct(messages, None, final_sys)
                return ChatResponse(response=final_res.choices[0].message.content, source=f"Google (Fallback)")
            
            return ChatResponse(response=response_message.content, source=f"Google (Fallback)")

    except Exception as e:
        error_str = str(e)
        print(f"All AI Providers Failed: {error_str}")
        return ChatResponse(response=f"⚠️ System Overload: Both OpenRouter and Google are busy. Please try again in 1 minute. ({error_str})", source="System Error")

        # Return a helpful message to the user if BOTH fail
        or_key = os.getenv("OPENROUTER_API_KEY", "")
        debug_info = f"OR Key: {or_key[:5]}..."
        
        error_msg = f"⚠️ **System Error**: Both OpenRouter and Google Fallback failed.\n\n" \
                    f"**Debug Info:** `{debug_info}`\n" \
                    f"**Error Details:** {error_str}\n\n" \
                    "Please check your OpenRouter API Key in Vercel Settings."
        print(f"All Providers failed. {debug_info} Error: {e}")
        return ChatResponse(response=error_msg, source="System Error")


# --- Chat History Endpoints ---

@router.get("/history", response_model=List[ChatMessageRead])
def get_chat_history(
    conversation_id: Optional[int] = None,
    session: Session = Depends(get_session),
    chat_service: ChatService = Depends(get_chat_service),
    user_id: str = Depends(get_current_user_id),
    limit: Optional[int] = 20
):
    """Get chat history for the authenticated user, optionally filtered by conversation."""
    return chat_service.get_user_history(session, user_id, limit, conversation_id)


@router.delete("/history")
def clear_chat_history(
    session: Session = Depends(get_session),
    chat_service: ChatService = Depends(get_chat_service),
    user_id: str = Depends(get_current_user_id)
):
    """Clear all chat history for the authenticated user."""
    count = chat_service.clear_history(session, user_id)
    return {"message": f"Cleared {count} messages", "count": count}


@router.post("/save-message")
def save_chat_message(
    message: ChatMessageCreate,
    session: Session = Depends(get_session),
    chat_service: ChatService = Depends(get_chat_service),
    user_id: str = Depends(get_current_user_id)
):
    """Save a chat message for the authenticated user."""
    saved_message = chat_service.save_message(session, message, user_id, message.conversation_id)
    return ChatMessageRead(
        id=saved_message.id,
        role=saved_message.role,
        content=saved_message.content,
        source=saved_message.source,
        timestamp=saved_message.timestamp,
        conversation_id=saved_message.conversation_id
    )
