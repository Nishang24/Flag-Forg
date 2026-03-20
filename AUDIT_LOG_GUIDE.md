# Audit Log & History Feature Documentation

## Overview

VoiceFlow now includes comprehensive audit logging to track all task changes. Perfect for:
- **Compliance & Auditing** - Prove who changed what and when
- **Debugging** - Track how tasks got into current state
- **Analytics** - Understand usage patterns
- **Forensics** - Investigate issues after the fact

---

## What Gets Logged

Every change to a task is recorded with:

| Field | Description | Example |
|-------|-------------|---------|
| **task_id** | Which task changed | `42` |
| **action** | Type of change | `created`, `updated`, `deleted`, `voice_command` |
| **field_name** | Which field changed | `status`, `priority`, `title` |
| **old_value** | Previous value | `"Todo"` |
| **new_value** | New value | `"Done"` |
| **source** | How change happened | `voice`, `api`, `workflow`, `ui` |
| **timestamp** | When it happened | `2026-03-19T10:45:32.123Z` |
| **details** | Additional context | `"Voice command: Create high priority..."` |

---

## Backend API Endpoints

### Get Task History
```bash
GET /tasks/{task_id}/history?limit=100
```
Returns complete audit history for a task.

**Response:**
```json
[
  {
    "id": 1,
    "task_id": 42,
    "action": "created",
    "field_name": "task",
    "old_value": null,
    "new_value": "Website Redesign",
    "source": "voice",
    "timestamp": "2026-03-19T10:00:00Z",
    "details": "Created via voice: 'Create high priority task...'"
  },
  {
    "id": 2,
    "task_id": 42,
    "action": "updated",
    "field_name": "status",
    "old_value": "Todo",
    "new_value": "InProgress",
    "source": "ui",
    "timestamp": "2026-03-19T10:05:00Z",
    "details": "status changed from 'Todo' to 'InProgress'"
  }
]
```

---

### Get Recent Activity
```bash
GET /audit/recent?limit=50
```
Get recent changes across all tasks (activity feed).

**Response:** List of 50 most recent audit log entries

---

### Get Audit Statistics
```bash
GET /audit/stats
```
Get summary statistics about audit logs.

**Response:**
```json
{
  "total_events": 127,
  "by_action": {
    "created": 42,
    "updated": 78,
    "deleted": 5,
    "voice_command": 2
  },
  "by_source": {
    "api": 45,
    "voice": 15,
    "workflow": 60,
    "ui": 7
  },
  "most_changed_field": "status"
}
```

---

### Export Audit Logs
```bash
GET /audit/export?task_id=42
```
Export audit logs as JSON for external analysis.

**Response:**
```json
{
  "export_date": "2026-03-19T10:45:00Z",
  "total_records": 42,
  "records": [
    {
      "id": 1,
      "task_id": 42,
      "action": "created",
      "field_name": "task",
      "old_value": null,
      "new_value": "Website Redesign",
      "source": "voice",
      "timestamp": "2026-03-19T10:00:00Z",
      "details": "Created via voice..."
    }
  ]
}
```

---

### Clear Audit Logs
```bash
DELETE /audit/clear/{task_id}
```
**Warning:** Permanently deletes all audit logs for a task!

---

## Data Sources Tracked

### 1. Voice Commands (source: "voice")
```
User says: "Create high priority task for bug fixing"
↓
Logged as:
- action: "created"
- source: "voice"
- details: "Created via voice: 'Create high priority...'"
```

### 2. API Calls (source: "api")
```
POST /tasks/ → Create task
PUT /tasks/{id} → Update task
DELETE /tasks/{id} → Delete task
↓
All logged with source: "api"
```

### 3. Workflow Actions (source: "workflow")
```
Task status changed → Workflow triggered
↓
Logged as action: "updated", source: "workflow"
```

### 4. UI Changes (source: "ui")
```
User clicks status button in Kanban board
↓
Logged with source: "ui"
```

---

## Frontend Integration

### AuditLogPanel Component

Shows task history in a collapsible panel:

```tsx
import { AuditLogPanel } from "@/components/AuditLog";

<AuditLogPanel taskId={42} />
```

Displays:
- Timeline of all changes
- Color-coded actions (created=green, updated=blue, deleted=red)
- Source icons (🎤 voice, ⚙️ api, ⚡ workflow, 🖱️ ui)
- Old value → New value
- Timestamps and details

### AuditStatsDashboard Component

Shows overall audit statistics:

```tsx
import { AuditStatsDashboard } from "@/components/AuditLog";

<AuditStatsDashboard />
```

Displays:
- Total events count
- Break down by action type
- Most frequently changed fields
- Auto-refreshes every 30 seconds

---

## Frontend API Functions

```typescript
// Get history for specific task
const history = await getTaskHistory(taskId, limit = 100);

// Get recent activity across all tasks
const recent = await getRecentActivity(limit = 50);

// Get audit statistics
const stats = await getAuditStats();

// Export logs as JSON
const exported = await exportAuditLogs(taskId?);

// Clear all logs for a task
await clearAuditLogs(taskId);
```

---

## Use Cases

### 1. Compliance & Audit Trail
Track all changes for regulatory compliance (GDPR, SOX, HIPAA, etc.)

```bash
# Export logs for auditor
curl http://localhost:8000/audit/export > audit_report.json
```

### 2. Debug Task Changes
Figure out how a task got into an unexpected state:

```bash
# What happened to task 42?
curl http://localhost:8000/tasks/42/history

# Shows: Created → Status changed to InProgress → Deleted → Recreated
```

### 3. Usage Analytics
Understand how users interact with the system:

```bash
# Get stats on voice vs API usage
curl http://localhost:8000/audit/stats

# Response shows: 60% voice commands, 40% API
```

### 4. Activity Dashboard
Show users a feed of recent changes:

```bash
# Load latest 50 changes
const recent = await getRecentActivity(50);
```

### 5. Forensics & Incident Response
Investigate security issues or data problems:

```bash
# Find all voice commands on 2026-03-19
curl http://localhost:8000/audit/recent?limit=1000 | grep voice
```

---

## Database Schema

The `task_audit_logs` table:

```sql
CREATE TABLE task_audit_logs (
  id INTEGER PRIMARY KEY,
  task_id INTEGER FOREIGN KEY,
  
  -- What changed
  action VARCHAR,              -- created, updated, deleted, voice_command
  field_name VARCHAR,          -- which field changed (nullable)
  old_value TEXT,              -- previous value (nullable)
  new_value TEXT,              -- new value (nullable)
  
  -- Metadata
  source VARCHAR DEFAULT 'api', -- voice, api, workflow, ui
  timestamp DATETIME,            -- when it happened
  details TEXT                  -- additional context
);
```

---

## Storing & Performance

- Audit logs are **automatically created** on every task change
- No manual intervention required
- Thread-safe (uses database transactions)
- Indexed on `task_id` and `timestamp` for fast queries
- Can handle 1000s of audit entries without performance degradation

---

## Best Practices

1. **Regular Exports**: Weekly export logs for compliance
   ```bash
   curl http://localhost:8000/audit/export > backup_$(date +%Y%m%d).json
   ```

2. **Monitor Activity**: Check audit stats regularly for anomalies
   ```bash
   # Spike in deletions? Investigate!
   curl http://localhost:8000/audit/stats
   ```

3. **Archive Old Logs**: Before clearing, export for archive
   ```bash
   # Export
   curl http://localhost:8000/audit/export > archive.json
   
   # Then clear
   curl -X DELETE http://localhost:8000/audit/clear/42
   ```

4. **Integrate with SIEM**: Send logs to Splunk, ELK, etc.
   ```bash
   # Continuously export and forward
   watch -n 60 'curl http://localhost:8000/audit/recent | forward-to-siem'
   ```

---

## Limitations & Future Enhancements

Current limitations:
- Audit logs are deleted when task is deleted (cascade)
- No user/identity tracking (all logged as "system")
- No filtering/search on audit logs yet

Future enhancements:
- User authentication → Log who made changes
- Advanced filtering & search on audit logs
- Retention policies (auto-archive after 90 days)
- Real-time WebSocket feed for live audit updates
- Diff view to see exact changes side-by-side
- Rollback functionality (undo changes)
- Alerts on suspicious activity

---

## Example: Complete Audit Trail

Here's a full example of how a task's audit trail evolves:

```
[10:00] ✅ CREATED (voice)
   "Website Redesign" created via voice command
   
[10:05] 🔄 UPDATED (ui)
   status: "Todo" → "InProgress"
   
[10:10] 🔄 UPDATED (api)
   priority: "Medium" → "High"
   
[10:15] ⚡ WORKFLOW TRIGGERED (workflow)
   status: "InProgress" (triggered Slack notification)
   
[10:20] 🔄 UPDATED (voice)
   status: "InProgress" → "Done" (via voice)
   
[10:25] ⚡ WORKFLOW TRIGGERED (workflow)
   status: "Done" (triggered completion notification)
```

Each entry is stored forever (until explicitly cleared) for compliance.

---

## Testing

Run the test suite to verify audit logging:

```bash
python test_api.py
```

The tests include:
- Audit creation on task creation
- Audit log on status changes
- Audit log on field updates
- Audit log on task deletion
- History retrieval
- Statistics generation
