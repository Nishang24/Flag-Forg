# 🧪 VoiceFlow - Testing & Verification Guide

## Frontend Health Check

After opening http://localhost:3000, verify:

1. **Dashboard loads** - "VoiceFlow" title visible
2. **Buttons are visible:**
   - "📊 Load Demo" (purple)
   - "+ Create Task" (white)
   - 🎤 Microphone button (red, bottom right)
3. **Search bar appears** at top
4. **Kanban board renders** with 3 columns: Open, Running, Finished
5. **No console errors** (F12 → Console tab should be clean)

---

## Backend Health Check

### Test 1: API Server Responds

```bash
# Any terminal
curl http://localhost:8000/docs

# Expected: Interactive API documentation page
```

### Test 2: Get All Tasks (empty initially)

**Windows PowerShell:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/tasks" -Method GET
$response.Content | ConvertFrom-Json
```

**Mac/Linux bash:**
```bash
curl http://localhost:8000/tasks
```

**Expected Output:**
```json
[]  # Empty array on first run
```

### Test 3: Seed Demo Data

**Windows PowerShell:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/seed-demo-data" -Method POST
$response.Content | ConvertFrom-Json
```

**Mac/Linux bash:**
```bash
curl -X POST http://localhost:8000/seed-demo-data
```

**Expected Output:**
```json
{
  "status": "success",
  "message": "Demo data seeded successfully",
  "task_count": 6
}
```

### Test 4: Verify Tasks Created

Run **Test 2** again - should now return 6 tasks:

```json
[
  {
    "id": 1,
    "title": "Setup project infrastructure",
    "description": "Initialize project structure",
    "status": "Todo",
    "priority": "High",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  ...
]
```

---

## Voice Processing Test

### Test 1: Verify OpenAI Connection

**Endpoint:** POST `/voice/process`  
**Payload:**
```json
{
  "transcript": "create a task to review pull requests",
  "user_id": 1
}
```

**Test with curl (Mac/Linux):**
```bash
curl -X POST http://localhost:8000/voice/process \
  -H "Content-Type: application/json" \
  -d '{"transcript":"create a task to review pull requests","user_id":1}'
```

**Expected Output:**
```json
{
  "status": "success",
  "extracted_intent": {
    "action": "create",
    "title": "Review pull requests",
    "priority": "Normal",
    "due_date": null
  },
  "task_created": true,
  "task_id": 7
}
```

⚠️ **If you get "API key error":**
- Check `backend/.env` has `OPENAI_API_KEY=sk-proj-...`
- Restart backend: kill and run `python main.py` again

---

## Complete End-to-End Workflow Test

### Step 1: Load Demo
```bash
curl -X POST http://localhost:8000/seed-demo-data
```

### Step 2: Create Task via Voice
```bash
curl -X POST http://localhost:8000/voice/process \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "create urgent task: implement oauth login by end of week",
    "user_id": 1
  }'
```

**Expected:** New task appears with high priority and due date set

### Step 3: Verify Task Created
```bash
curl http://localhost:8000/tasks
```

**Expected:** 7 tasks returned (6 demo + 1 new voice task)

### Step 4: Update Task Status
```bash
# Get latest task ID (should be 7)
curl -X PUT http://localhost:8000/tasks/7 \
  -H "Content-Type: application/json" \
  -d '{"status":"InProgress"}'
```

### Step 5: Delete Task
```bash
curl -X DELETE http://localhost:8000/tasks/7
```

### Step 6: View Audit Log
```bash
curl http://localhost:8000/audit/stats
```

**Expected:** Shows creation, update, and deletion in audit trail

---

## Frontend Integration Test

1. Open http://localhost:3000
2. Click "📊 Load Demo" → 6 tasks appear
3. Click 🎤 button
4. Say: *"Create task: test voice integration"*
5. Click "Process" button
6. **Verify:** New task appears in "Open" column
7. **Verify:** Search for "test" shows only the new task
8. **Verify:** Audit log shows the task creation

---

## Database Persistence Test

1. Create a task (via voice or form)
2. Restart backend: `Ctrl+C` then `python main.py`
3. Get all tasks: `curl http://localhost:8000/tasks`
4. **Verify:** Task still exists (data persisted in SQLite)

---

## Performance Benchmarks

### Expected Response Times

| Endpoint | Expected Time |
|----------|---|
| GET /tasks | < 100ms |
| POST /tasks | < 200ms |
| POST /voice/process | 1-3s (GPT-4o call) |
| PUT /tasks/{id} | < 200ms |
| DELETE /tasks/{id} | < 200ms |
| GET /audit/history/{id} | < 100ms |

---

## Automated Test Suite

### Backend Test Script

Create `backend/test_endpoints.py`:

```python
import requests
import json
from time import time

BASE_URL = "http://localhost:8000"
USER_ID = 1

def test_all():
    print("\n🧪 Testing VoiceFlow Backend...\n")
    
    # Test 1: Server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Backend is reachable")
    except:
        print("❌ Backend is NOT reachable on port 8000")
        return
    
    # Test 2: Get tasks (should be empty initially)
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"✅ GET /tasks: {len(response.json())} tasks")
    
    # Test 3: Seed demo data
    response = requests.post(f"{BASE_URL}/seed-demo-data")
    status = response.json()
    print(f"✅ POST /seed-demo-data: {status['message']}")
    
    # Test 4: Verify 6 tasks created
    response = requests.get(f"{BASE_URL}/tasks")
    tasks = response.json()
    print(f"✅ GET /tasks: {len(tasks)} tasks (expected 6)")
    
    # Test 5: Voice processing
    start = time()
    response = requests.post(f"{BASE_URL}/voice/process", json={
        "transcript": "create task: test automation",
        "user_id": USER_ID
    })
    elapsed = time() - start
    if response.status_code == 200:
        result = response.json()
        print(f"✅ POST /voice/process: {result['extracted_intent']['title']} ({elapsed:.2f}s)")
    else:
        print(f"❌ POST /voice/process failed: {response.text}")
    
    # Test 6: Get all tasks (should be 7 now)
    response = requests.get(f"{BASE_URL}/tasks")
    tasks = response.json()
    print(f"✅ GET /tasks: {len(tasks)} tasks (expected 7)")
    
    # Test 7: Audit stats
    response = requests.get(f"{BASE_URL}/audit/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ GET /audit/stats: {stats['total_changes']} total changes tracked")
    
    print("\n✨ All tests passed!\n")

if __name__ == "__main__":
    test_all()
```

**Run the test:**
```bash
cd backend
python test_endpoints.py
```

---

## Deployment Verification

After deploying to production:

1. **SSL/TLS Working** - HTTPS connection works
2. **API Responses** - Same as localhost tests
3. **Database** - PostgreSQL connection successful
4. **Environment Variables** - All .env vars set correctly  
5. **Voice Processing** - OpenAI API accessible
6. **Audit Logs** - Full history available
7. **Performance** - Response times acceptable

---

## Common Test Issues & Solutions

### Test Error: "Connection refused"
- ✅ Solution: Start backend with `python main.py`

### Test Error: "API key invalid"
- ✅ Solution: Check `backend/.env` has valid OpenAI key from https://platform.openai.com/api/keys

### Test Error: "Port 8000 already in use"
- ✅ Solution: `Get-Process python | Stop-Process -Force` then restart

### Test Slow (> 5 seconds response)
- ✅ Solution: Check OpenAI API quota not exceeded at https://platform.openai.com

---

## Regression Testing Checklist

Before each release, verify:

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Demo data seeds successfully (6 tasks)
- [ ] Voice processing returns correct parsed intent
- [ ] New tasks appear immediately in Kanban
- [ ] Search/filter works on titles and descriptions
- [ ] Audit log tracks all changes
- [ ] Drag-drop between columns updates status
- [ ] Delete task removes from board and audit log shows deletion
- [ ] Refresh browser → data persists from database
- [ ] No console errors (browser F12)
- [ ] No Python errors in terminal

---

See [FINAL_RUNNABLE_SETUP.md](FINAL_RUNNABLE_SETUP.md) for complete setup instructions.
