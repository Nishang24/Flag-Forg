# 🎤 VoiceFlow - Final Production Setup Guide

> **Complete End-to-End Setup for Hackathon Demo**  
> Get the entire voice-enabled task management system running in **5 minutes**

---

## ✅ Prerequisites

Before starting, ensure you have:

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.9+** - [Download](https://www.python.org/)
- **OpenAI API Key** - [Get from platform.openai.com](https://platform.openai.com/api/keys)
- **Git** (optional, for cloning)

**Verify installations:**
```powershell
# Windows PowerShell
node --version
python --version
# Should output: v18.x.x and Python 3.x.x
```

---

## 📦 Step 1: Backend Setup (5 minutes)

### 1.1 Navigate to Backend Directory
```powershell
cd .\backend
```

### 1.2 Create & Activate Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# If PowerShell blocks scripts, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Mac/Linux (bash/zsh):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Python Dependencies
```powershell
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn sqlalchemy python-dotenv openai requests python-multipart
```

### 1.4 Create `.env` File

Create a new file `backend/.env`:

```ini
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-xxx...

# Optional: Webhook integrations (leave empty to skip)
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=

# Database (SQLite for demo, PostgreSQL ready for production)
DATABASE_URL=sqlite:///./tasks.db

# FastAPI Settings
DEBUG=true
```

⚠️ **Security:** Never commit this file. Add to `.gitignore`.

### 1.5 Start the Backend Server

```powershell
# Make sure you're still in the backend directory (and venv is activated)
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

✅ **Backend is now running!** Keep this terminal open.

---

## 🎨 Step 2: Frontend Setup (3 minutes)

### 2.1 Open New Terminal/Tab

Open **new PowerShell/Terminal** (do NOT close backend terminal).

### 2.2 Navigate to Frontend Directory
```powershell
cd .\frontend
```

### 2.3 Install Node Dependencies
```powershell
npm install
```

**Expected output:**
```
added 400+ packages in 45s
```

### 2.4 Start Development Server

```powershell
npm run dev
```

**Expected output:**
```
> next dev

  ▲ Next.js 16.1.7
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 2.5s
```

✅ **Frontend is now running!** You can now open **http://localhost:3000** in your browser.

---

## 🚀 Step 3: Test the Complete Workflow

### 3.1 Load Demo Data

1. Open http://localhost:3000 in your browser
2. Click the **"📊 Load Demo"** button (purple button, top right)
3. You should see 6 demo tasks load into the Kanban board

**Demo tasks include:**
- "Setup project infrastructure" → Open
- "Implement voice recognition" → In Progress
- "Design UI components" → In Progress  
- "Write API documentation" → Open
- "Deploy to production" → Open
- "Complete testing" → Done

### 3.2 Test Voice Command

1. Allow microphone access when browser prompts
2. Click the **microphone button** (bottom right, red button)
3. Say: *"Create a task: schedule team meeting tomorrow at 2pm, priority high"*
4. Stop speaking or wait 2 seconds for recognition to complete
5. Click **"Process"** button
6. Watch the task appear in the Kanban board!

**Voice Command Examples:**
- *"Add task: review code changes, set priority to high"*
- *"Create task: fix login bug, mark as urgent"*
- *"Log task: update documentation by end of week"*

### 3.3 Test Manual Task Creation

1. Click **"+ Create Task"** button (white button, top right)
2. Fill in the form:
   - Title: "Design database schema"
   - Description: "Create ERD for user authentication"
   - Priority: High
   - Category: Backend
3. Click **"Create"**
4. Task appears in "Open" column

### 3.4 Test Search & Filter

1. Type in the **search bar**: "voice"
2. Watch tasks filter in real-time (should show 1 result)
3. Press **S** to focus search bar (keyboard shortcut)
4. Clear search and try filtering by category

### 3.5 Test Task Management

1. Click task card to see full details
2. Drag task to different column to change status:
   - Drag from "Open" → "Running" (changes status to In Progress)
   - Drag from "Running" → "Finished" (changes status to Done)
3. Click **trash icon** to delete task

### 3.6 View Audit Logs

1. Scroll to bottom of page
2. Click **"📋 Audit Log"** button
3. See complete history of all changes:
   - Who created/modified the task
   - What changed and when
   - Source of change (Voice, API, UI)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser (Frontend)                │
│  ┌─────────────────────────────────────────────┐   │
│  │  Next.js App (React 19, TypeScript)         │   │
│  │  - Voice Capture (Web Speech API)           │   │
│  │  - Kanban Board (Drag & Drop Ready)         │   │
│  │  - Search & Filter                          │   │
│  │  - Audit Log Viewer                         │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
                     │ (JSON)
                     ▼
┌─────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                   │
│  ┌─────────────────────────────────────────────┐   │
│  │  - 25+ REST Endpoints                       │   │
│  │  - Voice Processing (/voice/process)        │   │
│  │  - Task CRUD Operations                     │   │
│  │  - Workflow Automation (Slack/Discord)      │   │
│  │  - Audit Logging                            │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ SQL
                     │ API Keys (OpenAI)
                     ▼
┌─────────────────────────────────────────────────────┐
│              Data & Services Layer                   │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │ SQLite   │  │  OpenAI     │  │  Slack/      │   │
│  │ Database │  │  GPT-4o     │  │  Discord     │   │
│  │ (local)  │  │  (NLP)      │  │  Webhooks    │   │
│  └──────────┘  └─────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Environment Variables Reference

### Backend (.env file)

| Variable | Required? | Example | Purpose |
|----------|-----------|---------|---------|
| `OPENAI_API_KEY` | ✅ Yes | `sk-proj-...` | GPT-4o API access for voice parsing |
| `SLACK_WEBHOOK_URL` | ❌ No | `https://hooks.slack.com/...` | Send task notifications to Slack |
| `DISCORD_WEBHOOK_URL` | ❌ No | `https://discord.com/api/webhooks/...` | Send task notifications to Discord |
| `DATABASE_URL` | ⏸️ Optional | `sqlite:///./tasks.db` | Database connection (default: SQLite) |
| `DEBUG` | ⏸️ Optional | `true` | Enable debug logging |

---

## 📱 API Endpoints Reference

### Tasks
- **GET** `/tasks` - Fetch all tasks
- **POST** `/tasks` - Create new task
- **PUT** `/tasks/{task_id}` - Update task
- **DELETE** `/tasks/{task_id}` - Delete task

### Voice Processing
- **POST** `/voice/process` - Process voice transcript

### Workflows
- **GET** `/workflows` - Get all workflow triggers
- **POST** `/workflows` - Create workflow trigger
- **DELETE** `/workflows/{trigger_id}` - Delete trigger

### Audit Logs
- **GET** `/audit/history/{task_id}` - Get task changes
- **GET** `/audit/stats` - Get audit statistics
- **POST** `/audit/export` - Export audit logs as CSV

### Demo
- **POST** `/seed-demo-data` - Load demo tasks

---

## ❌ Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```powershell
# Find process using port 8000
Get-Process | Where-Object { $_.Ports -eq 8000 }

# Kill the process
Get-Process python | Stop-Process -Force

# Try again
python main.py
```

**Error: "ModuleNotFoundError: No module named 'fastapi'"**
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "OpenAI API key error"**
- Go to https://platform.openai.com/api/keys
- Create new API key
- Add to `backend/.env`: `OPENAI_API_KEY=sk-...`
- Restart backend

---

### Frontend Won't Start

**Error: "Cannot find module 'next'"**
```powershell
# Make sure you're in frontend directory
cd ./frontend

# Clear node_modules and reinstall
rm -r node_modules
rm package-lock.json
npm install
```

**Error: "Port 3000 already in use"**
```powershell
# Start on different port
npm run dev -- --port 3001

# Then visit http://localhost:3001
```

---

### Voice Recognition Not Working

**Issue: "Speech Recognition not supported"**
- Use **Chrome, Edge, or Safari** browser (Firefox not supported)
- Ensure you allowed microphone access
- Check https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API for browser support

**Issue: Voice recognized but no task created**
- Check browser console for errors (F12)
- Verify OpenAI API key is set in backend `.env`
- Check backend logs for `/voice/process` errors
- Try simpler voice command: *"Create task: test"*

---

### Database Connection Issues

**Error: "Database is locked"**
```python
# Reset database
import os
os.remove("tasks.db")
# Restart backend - new database will be created
```

---

## 🎯 Demo Scenario (10 minutes)

Perfect for hackathon judges:

1. **Setup (1 min)** - Start both backend and frontend
2. **Load Demo (1 min)** - Click "Load Demo" to show existing tasks
3. **Voice Demo (3 min)**:
   - Say: *"Create urgent task: implement payment integration"*
   - Show task appears in board
   - Use search to find it
4. **Manual Demo (2 min)**:
   - Create task via form
   - Drag task between columns
   - Click delete to remove
5. **Audit Trail (2 min)**:
   - Open audit log
   - Show all changes tracked with timestamps
   - Explain source tracking (Voice vs API)

**Total demo time: ~10 minutes**

---

## 📚 Project Structure

```
hackathon/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py              # SQLAlchemy database models
│   ├── schemas.py             # Pydantic validation schemas
│   ├── voice_parser.py        # GPT-4o voice processing
│   ├── workflow_engine.py     # Slack/Discord automation
│   ├── audit_logger.py        # Audit trail functionality
│   ├── database.py            # Database session management
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (CREATE THIS)
│   ├── venv/                  # Python virtual environment
│   └── tasks.db               # SQLite database (auto-created)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main dashboard component
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── lib/
│   │   └── api.ts             # API client functions
│   ├── components/
│   │   └── ...                # Reusable components
│   ├── package.json           # Node dependencies
│   ├── next.config.ts         # Next.js configuration
│   ├── tsconfig.json          # TypeScript configuration
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── node_modules/          # Node packages
│
└── Documentation files
    ├── FINAL_RUNNABLE_SETUP.md (this file)
    ├── PROJECT_STATUS.md
    ├── SETUP_GUIDE.md
    └── API documentation
```

---

## ✨ Features Demonstration

### Voice-to-Task Pipeline
```
"Create task: review pull requests" (spoken)
        ↓
Web Speech API captures audio
        ↓
GPT-4o parses intent: title + priority + due date
        ↓
Backend creates task with audit log
        ↓
Real-time UI update via React state
```

### Audit Trail Example
```
Task: "Implement OAuth"
Timeline:
  • Created at 10:15 AM via Voice Command
  • Priority changed: Normal → High at 10:20 AM
  • Status updated: Todo → In Progress at 10:25 AM
  • Status updated: In Progress → Done at 10:50 AM
```

---

## 🚨 Important Notes

1. **First Time Setup Takes ~10 minutes** for dependencies
2. **API Key Required** - VoiceFlow needs OpenAI API key to work
3. **Microphone Access** - Browser will ask for permission (allow it)
4. **Port Requirements**:
   - Backend: 8000 (must be free)
   - Frontend: 3000 (must be free)
5. **Keep Both Terminals Open** - Both services must run simultaneously
6. **Browser Support** - Voice features work in Chrome/Edge/Safari only

---

## 🎊 You're Ready!

Your complete voice-enabled task management system is now running!

**Next Steps:**
1. Open http://localhost:3000
2. Click "Load Demo" to see example tasks
3. Try voice commands
4. Explore the Kanban board
5. Check audit trails

**Questions or Issues?** Check the Troubleshooting section above.

---

## 📊 Project Statistics

- **Backend:** 1000+ lines of code (FastAPI + SQLAlchemy)
- **Frontend:** 800+ lines of code (React + TypeScript)
- **API Endpoints:** 25+ endpoints
- **Database Models:** 4 models (User, Task, WorkflowTrigger, TaskAuditLog)
- **UI Components:** 15+ reusable components
- **External APIs:** 2 (OpenAI GPT-4o, Slack/Discord)
- **Features:** Voice processing, Kanban board, Audit logs, Workflow automation

---

## 📞 Support

If you encounter issues:

1. **Check Troubleshooting section** above for common problems
2. **Verify API keys** are correctly configured
3. **Ensure ports 3000 & 8000 are free**
4. **Check browser console** (F12) for JavaScript errors
5. **Check backend logs** for Python errors

**Default test user:** Auto-created on first run  
**Demo data:** Available via "Load Demo" button

---

**Happy voice-commanding! 🎤✨**
