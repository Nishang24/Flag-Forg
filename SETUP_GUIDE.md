# VoiceFlow Setup Guide - National Hackathon Ready

## 🚀 Quick Start (5 minutes)

### 1. Backend Setup

```powershell
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your keys
Copy-Item .env.example .env

# Edit .env and add:
# - OPENAI_API_KEY from https://platform.openai.com/api-keys
# - SLACK_WEBHOOK_URL (optional) - for Slack notifications
# - DISCORD_WEBHOOK_URL (optional) - for Discord notifications

# Start backend
python -m uvicorn main:app --reload
```

Backend runs on: **http://localhost:8000**

### 2. Frontend Setup

```powershell
# New terminal
cd frontend

# Install dependencies  
npm install

# Start dev server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 🎤 Demo Workflow

### Step 1: Load Demo Data
1. Go to http://localhost:3000
2. Click **"Load Demo"** button (purple)
3. Kanban board fills with realistic tasks

### Step 2: Test Voice Commands
Click the blue **🎤** mic button and say:
- **"Create a high priority task for bug fixing due tomorrow"**
- **"Create task database optimization"**  
- **"Delete the navigation bug task"**

### Step 3: Update Task Status
- Click **"Start"** to move task from "Open" → "Running"
- Click **"Complete"** to move task from "Running" → "Finished"
- Watch workflow automation trigger (if webhooks configured)

### Step 4: Add Workflow Automation (Slack/Discord)

**For Slack:**
1. Create Slack Workspace
2. Go to api.slack.com/apps
3. Create New App → From scratch
4. Enable "Incoming Webhooks"
5. Add New Webhook to your channel
6. Copy webhook URL to `.env` as `SLACK_WEBHOOK_URL`
7. Restart backend

**For Discord:**
1. Open Server Settings → Webhooks
2. Create Webhook
3. Copy URL to `.env` as `DISCORD_WEBHOOK_URL`
4. Restart backend

Now when tasks complete, webhook notifications will auto-send!

---

## 📊 API Endpoints

### Tasks
- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Voice
- `POST /voice/process` - Process voice command

### Workflows
- `POST /workflows/` - Create workflow trigger
- `GET /workflows/{task_id}` - Get task workflows  
- `DELETE /workflows/{id}` - Delete workflow

### Demo
- `POST /seed-demo-data` - Load demo data
- `GET /health` - Health check

---

## 🛠️ Tech Stack

**Frontend:**
- Next.js 16 (React 19)
- Tailwind CSS
- Framer Motion (animations)
- Web Speech API (voice capture)

**Backend:**
- FastAPI
- SQLAlchemy ORM
- OpenAI GPT-4o (intent parsing)
- SQLite (demo) / PostgreSQL (production)

---

## 🐛 Troubleshooting

**"Speech Recognition not supported"**
- Use Chrome, Edge, or Safari
- Firefox has limited support

**"OpenAI API error"**
- Check OPENAI_API_KEY is valid
- Verify .env file in backend folder

**"Webhook failed"**
- Verify webhook URLs in .env
- Test webhook in Slack/Discord settings

**Backend won't start**
```powershell
# Clear database and restart
cd backend
rm sql_app.db
python -m uvicorn main:app --reload
```

---

## 🎯 For Hackathon Judges

### Live Demo Script (2 minutes)

1. **Show Voice Command Processing:**
   - Click mic → Say "Create high-priority task for website redesign"
   - Show task appears instantly on board with correct priority

2. **Show Workflow Automation:**
   - Click "Complete" on a task
   - Show Slack/Discord notification appears

3. **Show AI Intelligence:**
   - Open browser console (F12)
   - Say a complex command like "Mark my critical bug fix as done by tomorrow"
   - Show GPT-4o parsed it correctly (check console logs)

4. **Emphasize Accessibility:**
   - "Complete task management using only voice"
   - "Zero UI operations - perfect for motor/visual impairments"

### Key Selling Points

✅ **Zero-UI Voice Operations** - Control everything by voice  
✅ **AI-Powered Intent Parsing** - Understands natural language  
✅ **Automatic Workflows** - Tasks trigger real notifications  
✅ **Enterprise-Ready** - Real database, proper API, webhook integrations  
✅ **Accessibility-First** - Designed for users with disabilities  

---

## 📝 Next Steps

- [ ] Add database migrations (Alembic)
- [ ] Add user authentication (Auth0/Firebase)
- [ ] Implement drag-and-drop task moving
- [ ] Add task due date/calendar view
- [ ] Add collaborative features (team tasks)
- [ ] Deploy to AWS/Vercel
