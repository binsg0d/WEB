from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from itertools import count
from typing import Annotated, Literal
from pydantic import Field, AfterValidator, field_validator
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI(title="TaskBoard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    expose_headers=["X-Total-Count"],
)
PROJECTS: dict[int, dict] = {
    1: {"id": 1, "name": "TaskBoard", "description": "..."},
    2: {"id": 2, "name": "Praca dyplomowa", "description": None},
}
USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Jan Kowalski", "email": "jan@example.com"},
    2: {"id": 2, "name": "Anna Nowak", "email": "anna@example.com"},
}
TASKS: dict[int, dict] = {
    1: {
        "id": 1,
        "project_id": 1,
        "title": "Przygotować środowisko",
        "status": "done",
        "priority": "high",
        "assignee_id": None,
    },
    2: {
        "id": 1 + 1,
        "project_id": 1,
        "title": "Przeczytać RFC 9110",
        "status": "open",
        "priority": "medium",
        "assignee_id": None,
    },
    3: {
        "id": 3,
        "project_id": 1,
        "title": "Zaprojektować API",
        "status": "open",
        "priority": "low",
        "assignee_id": None,
    },
}
next_project_id = count(3)
next_task_id = count(5)
NEXT_ID = 4

def not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(
            "Wartość nie może składać się z samych białych znaków"
        )
    return value

Title = Annotated[
    str,
    Field(min_length=1, max_length=200),
    AfterValidator(not_blank),
]

Status = Literal["open", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]

def validate_assignee(assignee_id: int | None):
    if assignee_id is not None and assignee_id not in USERS:
        raise invalid_reference("assignee_id", f"Użytkownik {assignee_id} nie istnieje")
class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: int
    title: Title
    status: Status = "open"
    priority: Priority = "medium"
    assignee_id: int | None = None

class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    status: Status
    priority: Priority
    assignee_id: int | None


class TaskIn(BaseModel):
    title: str
    status: str = "open"
    priority: str = "medium"

class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee_id: int | None = None
    @field_validator("title", "status", "priority")
    @classmethod
    def reject_null(cls, value: str | None) -> str:
            if value is None:
                raise ValueError("Pole nie może mieć wartości null")
            return value
class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Title | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def reject_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Pole nie może mieć wartości null")
        return value

def check_project_has_tasks(project_id: int):
    has_tasks = any(task.get("project_id") == project_id for task in TASKS.values())
    if has_tasks:
        raise HTTPException(
            status_code=409,
            detail="Nie można usunąć projektu, który posiada przypisane zadania"
        )

class UserOut(BaseModel):
    id: int
    name: str

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    task_count: int
class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    errors: list[dict] | None = None
def problem(status: int, detail: str, errors: list | None = None, headers: dict | None = None) -> JSONResponse:
    content = Problem(
        title="Błąd" if status < 500 else "Błąd serwera",
        status=status,
        detail=detail,
        errors=errors,
    ).model_dump(exclude_none=True)
    
    return JSONResponse(status_code=status, content=content, headers=headers)
# Słownik wspólnych odpowiedzi błędów w formacie Problem Details
RESPONSES_400_422 = {
    400: {"model": Problem, "description": "Niepoprawny format żądania (np. błąd JSON)"},
    422: {"model": Problem, "description": "Błąd walidacji danych wejściowych"},
}

RESPONSES_404 = {
    404: {"model": Problem, "description": "Zasób nie został znaleziony"},
}

RESPONSES_409 = {
    409: {"model": Problem, "description": "Konflikt (np. duplikacja unikalnej nazwy)"},
}

def find_by_title(title: str) -> dict | None:
    for task in TASKS.values():
        if task["title"] == title:
            return task
    return None


@app.get("/")
def root():
    return {"message": "Hello Web"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(
    response: Response, 
    status: str | None = None, 
    project_id: int | None = None,
    assignee_id: int | None = None,
    limit: int = 20
):
    items = list(TASKS.values())
    if status is not None:
        items = [task for task in items if task["status"] == status]
    if project_id is not None:
        items = [task for task in items if task.get("project_id") == project_id]
    if assignee_id is not None:
        items = [task for task in items if task.get("assignee_id") == assignee_id]

    response.headers["X-Total-Count"] = str(len(items))
    return {"items": items[:limit], "total": len(items)}


@app.get("/tasks/{task_id}",responses={
        404: RESPONSES_404[404],
    })
def get_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Zadanie nie istnieje")
    return task


@app.post("/tasks", status_code=201, response_model=TaskOut,responses={
        **RESPONSES_400_422,
        409: RESPONSES_409[409],
    })
def create_task(payload: TaskCreate, response: Response):
    if payload.project_id not in PROJECTS:
        raise invalid_reference(
            "project_id",
            f"Projekt {payload.project_id} nie istnieje"
        )
    validate_assignee(payload.assignee_id)
    check_unique_title(payload.project_id, payload.title)

    task_id = next(next_task_id)
    task = {"id": task_id, **payload.model_dump()}
    TASKS[task_id] = task

    response.headers["Location"] = f"/tasks/{task_id}"
    return task
def invalid_reference(field: str, detail: str):
    return HTTPException(status_code=422, detail=detail)

@app.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate):
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Projekt nie istnieje")
    
    changes = payload.model_dump(exclude_unset=True)
    PROJECTS[project_id].update(changes)
    
    # Przeliczamy task_count dla modelu odpowiedzi
    task_count = sum(1 for t in TASKS.values() if t.get("project_id") == project_id)
    return {**PROJECTS[project_id], "task_count": task_count}


@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int):
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Projekt nie istnieje")
    
    # Sprawdzamy, czy projekt ma zadania – jeśli tak, zwracamy 409
    check_project_has_tasks(project_id)
    
    del PROJECTS[project_id]

def check_unique_title(
    project_id: int,
    title: str,
    exclude_task_id: int | None = None,
):
    for task_id, task in TASKS.items():
        if (
            task.get("project_id") == project_id
            and task["title"] == title
            and task_id != exclude_task_id
        ):
            raise HTTPException(
                status_code=409,
                detail="Tytuł zadania już istnieje w tym projekcie",
            )


def get_task_or_404(task_id: int) -> dict:
    task = TASKS.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Zadanie nie istnieje",
        )

    return task


@app.put("/tasks/{task_id}")
def replace_task(task_id: int, payload: TaskIn):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Zadanie nie istnieje")
    task = {
        "id": task_id,
        "title": payload.title,
        "status": payload.status,
        "priority": payload.priority,
    }
    TASKS[task_id] = task
    return task

@app.patch("/tasks/{task_id}", response_model=TaskOut,responses={
        **RESPONSES_400_422,
        404: RESPONSES_404[404],
        409: RESPONSES_409[409],
    })
def update_task(task_id: int, payload: TaskUpdate):
    task = get_task_or_404(task_id)
    changes = payload.model_dump(exclude_unset=True)
    if "assignee_id" in changes:
        validate_assignee(changes["assignee_id"])
    if "title" in changes:
        check_unique_title(
            task["project_id"],
            changes["title"],
            task_id
        )

    task.update(changes)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Zadanie nie istnieje")
    del TASKS[task_id]

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem(
        status=exc.status_code, 
        detail=str(exc.detail), 
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    if any(error["type"] == "json_invalid" for error in exc.errors()):
        return problem(400, "Ciało żądania nie jest poprawnym dokumentem JSON")
    
    # Przypisujemy błędy walidacji do zmiennej przed użyciem
    errors = exc.errors()
    return problem(422, "Dane wejściowe nie spełniają kontraktu API", errors=errors)