const API_URL = "http://localhost:8000";

const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('vf_token') : null;

const getHeaders = (isJson = true) => {
  const headers: Record<string, string> = {};
  if (isJson) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
};

export async function getTasks() {
  const res = await fetch(`${API_URL}/tasks/`, { headers: getHeaders(false) });
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function createTask(task: { title: string; description?: string; priority?: string }) {
  const res = await fetch(`${API_URL}/tasks/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error("Failed to create task");
  return res.json();
}

export async function updateTask(id: number, task: any) {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

export async function deleteTask(id: number) {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: "DELETE",
    headers: getHeaders(false),
  });
  if (!res.ok) throw new Error("Failed to delete task");
  return res.json();
}

export async function processVoiceCommand(transcription: string) {
  const res = await fetch(`${API_URL}/voice/process`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ transcription }),
  });
  if (!res.ok) throw new Error("Failed to process voice command");
  return res.json();
}

export async function seedDemoData() {
  const res = await fetch(`${API_URL}/seed-demo-data`, {
    method: "POST",
    headers: getHeaders(false),
  });
  if (!res.ok) throw new Error("Failed to seed demo data");
  return res.json();
}

// ========== AUDIT LOG ENDPOINTS ==========

export async function getTaskHistory(taskId: number, limit: number = 100) {
  const res = await fetch(`${API_URL}/tasks/${taskId}/history?limit=${limit}`, { headers: getHeaders(false) });
  if (!res.ok) throw new Error("Failed to fetch task history");
  return res.json();
}

export async function getRecentActivity(limit: number = 50) {
  const res = await fetch(`${API_URL}/audit/recent?limit=${limit}`, { headers: getHeaders(false) });
  if (!res.ok) throw new Error("Failed to fetch recent activity");
  return res.json();
}

export async function getAuditStats() {
  const res = await fetch(`${API_URL}/audit/stats`, { headers: getHeaders(false) });
  if (!res.ok) throw new Error("Failed to fetch audit stats");
  return res.json();
}

export async function exportAuditLogs(taskId?: number) {
  const url = taskId 
    ? `${API_URL}/audit/export?task_id=${taskId}`
    : `${API_URL}/audit/export`;
  const res = await fetch(url, { headers: getHeaders(false) });
  if (!res.ok) throw new Error("Failed to export audit logs");
  return res.json();
}

export async function clearAuditLogs(taskId: number) {
  const res = await fetch(`${API_URL}/audit/clear/${taskId}`, {
    method: "DELETE",
    headers: getHeaders(false),
  });
  if (!res.ok) throw new Error("Failed to clear audit logs");
  return res.json();
}
