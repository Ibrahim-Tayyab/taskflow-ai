# TaskFlow - AI-Powered Todo App (Phase 3 Complete)

![TaskFlow Phase 3](public/assets/phase3-complete.png)

**TaskFlow** is the next generation of task management, powered by **Google Gemini 2.0**. It combines a beautiful, glassmorphism-inspired UI with an intelligent AI agent that acts as your personal productivity assistant.

## ✨ Key Features (Phase 3)

*   **🤖 AI Chatbot Agent**: Just say "Remind me to call John tomorrow at 5 PM" and let the AI handle the rest.
*   **🧠 Intelligent Parsing**: Powered by Google Gemini 2.0 Flash for accurate intent recognition.
*   **🔌 MCP Tools Protocol**: Built on the Model Context Protocol to standardize AI-System interactions.
*   **� Bank-Grade Security**: Full JWT Authentication with HTTP-Only cookies.
*   **⚡ Modern Stack**:
    *   **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion.
    *   **Backend**: FastAPI (Python), SQLModel, Pydantic.
    *   **Database**: Neon Serverless Postgres.

---

## � Easy Setup Guide

### 1. Prerequisites
*   Node.js 18+
*   Python 3.10+
*   A Google Cloud Project (for Gemini API)

### 2. Clone & Install
```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow

# Install Frontend Dependencies
npm install

# Install Backend Dependencies
pip install -r api/requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the root directory:

```ini
# Database (Neon Postgres)
DATABASE_URL="postgresql://user:pass@ep-rest-123.aws.neon.tech/neondb?sslmode=require"

# AI Configuration
GOOGLE_API_KEY="your_gemini_api_key_here"
OPENROUTER_API_KEY="optional_if_using_openrouter"

# Authentication
BETTER_AUTH_SECRET="your_random_secret_string"
BETTER_AUTH_URL="http://localhost:3000"
```

### 4. Run Locally
We have a unified start command:
```bash
npm run dev
```
> This starts the Next.js frontend on `http://localhost:3000` and FastAPI backend on `http://localhost:8000`.

---

## 🌐 Deployment (Vercel)

This project is optimized for **Vercel**.
1.  Push to GitHub.
2.  Import project in Vercel.
3.  Add the **Environment Variables** (from step 3 above) in Vercel Settings.
4.  Deploy! 🚀

---

## 📸 Screenshots

| Dashboard | AI Chat Interface |
|:---:|:---:|
| *(Add dashboard screenshot here)* | *(Add chat screenshot here)* |

---
**Hackathon II • Phase 3 Submission**
*Built with ❤️ by Ibrahim Tayyab*