const API_URL = "http://localhost:8001";

// ============= TASKS =============
export async function getTasks(status?: string) {
  const url = new URL(`${API_URL}/tasks`);
  if (status) url.searchParams.append("status", status);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function createTask(task: any) {
  const res = await fetch(`${API_URL}/tasks`, {
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

// ============= WORKERS =============
export async function getWorkers(department?: string) {
  const url = new URL(`${API_URL}/workers`);
  if (department) url.searchParams.append("department", department);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch workers");
  return res.json();
}

export async function createWorker(worker: any) {
  const res = await fetch(`${API_URL}/workers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(worker),
  });
  if (!res.ok) throw new Error("Failed to create worker");
  return res.json();
}

export async function updateWorker(id: number, worker: any) {
  const res = await fetch(`${API_URL}/workers/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(worker),
  });
  if (!res.ok) throw new Error("Failed to update worker");
  return res.json();
}

export async function deleteWorker(id: number) {
  const res = await fetch(`${API_URL}/workers/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete worker");
  return res.json();
}

// ============= INVENTORY =============
export async function getInventory(category?: string) {
  const url = new URL(`${API_URL}/inventory`);
  if (category) url.searchParams.append("category", category);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch inventory");
  return res.json();
}

export async function createInventoryItem(item: any) {
  const res = await fetch(`${API_URL}/inventory`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  if (!res.ok) throw new Error("Failed to create inventory item");
  return res.json();
}

export async function updateInventoryItem(id: number, item: any) {
  const res = await fetch(`${API_URL}/inventory/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  if (!res.ok) throw new Error("Failed to update inventory item");
  return res.json();
}

export async function addInventoryTransaction(itemId: number, transaction: any) {
  const res = await fetch(`${API_URL}/inventory/${itemId}/transaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(transaction),
  });
  if (!res.ok) throw new Error("Failed to record transaction");
  return res.json();
}

// ============= ASSIGNMENTS =============
export async function getAssignments() {
  const res = await fetch(`${API_URL}/assignments`);
  if (!res.ok) throw new Error("Failed to fetch assignments");
  return res.json();
}

export async function createAssignment(assignment: any) {
  const res = await fetch(`${API_URL}/assignments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(assignment),
  });
  if (!res.ok) throw new Error("Failed to create assignment");
  return res.json();
}

// ============= VOICE COMMANDS =============
export async function processVoiceCommand(transcription: string) {
  const res = await fetch(`${API_URL}/voice/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcription }),
  });
  if (!res.ok) throw new Error("Failed to process voice command");
  return res.json();
}

// ============= AUDIT LOGS =============
export async function getAuditLogs(entityType?: string) {
  const url = new URL(`${API_URL}/audit-logs`);
  if (entityType) url.searchParams.append("entity_type", entityType);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function getTaskAudit(taskId: number) {
  const res = await fetch(`${API_URL}/task-audit/${taskId}`);
  if (!res.ok) throw new Error("Failed to fetch task audit");
  return res.json();
}

// ============= HEALTH CHECK =============
export async function healthCheck() {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Service unavailable");
  return res.json();
}
