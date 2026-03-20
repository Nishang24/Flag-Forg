const API_URL = "http://localhost:8000";

export async function getTasks() {
  const res = await fetch(`${API_URL}/tasks/`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function createTask(task: { title: string; description?: string; priority?: string }) {
  const res = await fetch(`${API_URL}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error("Failed to create task");
  return res.json();
}

export async function updateTask(id: number, task: any) {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

export async function deleteTask(id: number) {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete task");
  return res.json();
}

export async function processVoiceCommand(transcription: string) {
  const res = await fetch(`${API_URL}/voice/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcription }),
  });
  if (!res.ok) throw new Error("Failed to process voice command");
  return res.json();
}

export async function seedDemoData() {
  const res = await fetch(`${API_URL}/seed-demo-data`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to seed demo data");
  return res.json();
}

export async function getTaskHistory(taskId: number, limit: number = 100) {
  const res = await fetch(`${API_URL}/tasks/${taskId}/history?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch task history");
  return res.json();
}

export async function getRecentActivity(limit: number = 50) {
  const res = await fetch(`${API_URL}/audit/recent?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch recent activity");
  return res.json();
}

export async function getAuditStats() {
  const res = await fetch(`${API_URL}/audit/stats`);
  if (!res.ok) throw new Error("Failed to fetch audit stats");
  return res.json();
}

export async function exportAuditLogs(taskId?: number) {
  const url = taskId 
    ? `${API_URL}/audit/export?task_id=${taskId}`
    : `${API_URL}/audit/export`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to export audit logs");
  return res.json();
}

export async function clearAuditLogs(taskId: number) {
  const res = await fetch(`${API_URL}/audit/clear/${taskId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to clear audit logs");
  return res.json();
}
