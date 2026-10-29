const API_URL = "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(status, message, errors = []) {
    super(message);
    this.status = status;
    this.errors = errors; // tablica obiektów z opisem błędów z Pydantica
  }
}
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
  const problem = await response.json().catch(() => null);
  throw new ApiError(
  response.status,
  problem?.detail ?? response.statusText,
  problem?.errors ?? [],
  );
  }
  return response;
}

export async function fetchTasks(status) {
  const params = new URLSearchParams();
  if (status) {
    params.set("status", status);
  }
  const query = params.toString();
  const response = await request(query ? `/tasks?${query}` : "/tasks");
  const data = await response.json();
  return {
    items: data.items,
    totalHeader: response.headers.get("X-Total-Count"),
  };
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
  await request(`/tasks/${taskId}`, { method: "DELETE" });
}
