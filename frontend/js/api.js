const API_URL = "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(response.status, detail);
  }
  return response;
}

export async function fetchTasks() {
  const response = await request("/tasks");
  const data = await response.json();
  return data.items;
}

export async function createTask(task) {
  const response = await request("/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  return response.json();
}
export async function deleteTask(taskId) {
  await request(`/tasks/${taskId}`, {
    method: "DELETE",
  });
}