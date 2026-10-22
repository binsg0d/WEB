from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class TaskIn(BaseModel):
    title: str
    status: str = "open"
    priority: str = "medium"

app = FastAPI(title="TaskBoard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["GET", "POST"],
)

@app.post("/tasks", status_code=201)
def create_task(payload: TaskIn, response: Response):
    global NEXT_ID

    task = {
        "id": NEXT_ID,
        "title": payload.title,
        "status": payload.status,
        "priority": payload.priority,
    }
    TASKS[NEXT_ID] = task
    response.headers["Location"] = f"/tasks/{NEXT_ID}"
    NEXT_ID += 1
    return task

@app.get("/")
def root():
    return {"message": "Hello Web"}

@app.get("/health")
def root():
    return {"status": "ok"}

TASKS: dict[int, dict] = {
    1: {"id" : 1, "title": "Przygotować Środowisko",
        "status": "done", "priority": "high"},
    2: {"id" : 2, "title": "Przeczyać RFC 9110",
        "status": "open", "priority": "medium"},
}

NEXT_ID = 3 

@app.get("/tasks")
def list_tasks(status: str | None = None, limit: int = 20):
    items = list(TASKS.values())
    if status is not None:
        items = [t for t in items if t["status"] == status]
    return {"items": items[:limit], "total": len(items)}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    del TASKS[task_id]
