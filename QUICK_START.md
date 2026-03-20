# 🚀 VoiceFlow - Quick Start (2 Minutes)

## One-Command Setup (Windows)

```powershell
# Simply run this in your hackathon folder
.\start.bat
```

This automatically:
- Creates Python virtual environment
- Installs all dependencies
- Starts backend on port 8000
- Starts frontend on port 3000

## One-Command Setup (Mac/Linux)

```bash
# Simply run this in your hackathon folder
chmod +x start.sh
./start.sh
```

---

## Manual Setup (If Scripts Don't Work)

### Terminal 1: Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create .env file with your OpenAI API key
python main.py
```

### Terminal 2: Frontend
```powershell
cd frontend
npm install
npm run dev
```

---

## Access the Application

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000  
- **API Docs:** http://localhost:8000/docs

---

## First Time Setup Checklist

- [ ] Have OpenAI API key? ([Get here](https://platform.openai.com/api/keys))
- [ ] Created `backend/.env` with API key
- [ ] Backend running (shows "Uvicorn running on http://127.0.0.1:8000")
- [ ] Frontend running (shows "Ready in X.Xs")
- [ ] Opened http://localhost:3000 in browser
- [ ] Clicked "Load Demo" to see sample tasks

---

## Immediate Demo (for Judges)

1. Load demo data (click purple button)
2. Say: *"Create task: implement oauth login"*
3. Watch it appear in Kanban board
4. Drag it between columns
5. Open audit log to show tracking

**Total demo time: 3-5 minutes**

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install from https://python.org |
| Node not found | Install from https://nodejs.org |
| Port 8000 in use | `Get-Process python \| Stop-Process -Force` |
| Port 3000 in use | `npm run dev -- --port 3001` |
| API key error | Check `backend/.env` has valid `OPENAI_API_KEY` |
| Voice not working | Use Chrome/Edge/Safari browser |

---

See [FINAL_RUNNABLE_SETUP.md](FINAL_RUNNABLE_SETUP.md) for complete documentation.
