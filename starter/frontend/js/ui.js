const taskList = document.querySelector("#task-list");
const listStatus = document.querySelector("#list-status");
const formError = document.querySelector("#form-error");
const total = document.querySelector("#total");

function createTaskItem(task) {
  const item = document.createElement("li");
  item.className = "task";
  item.dataset.id = task.id;
  if (task.status === "done") {
    item.classList.add("task-done");
  }

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;

  const priority = document.createElement("span");
  priority.className = `badge badge-${task.priority}`;
  priority.textContent = task.priority;

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "task-delete";
  deleteButton.dataset.action = "delete";
  deleteButton.textContent = "Usuń";

  item.append(title, priority, deleteButton);
  return item;
}

export function renderTasks(tasks) {
  taskList.replaceChildren(...tasks.map(createTaskItem));
}

export function renderTotal(totalHeader) {
  total.textContent = totalHeader === null ? "" : `Pasujących zadań: ${totalHeader}`;
}

export function showListLoading() {
  taskList.setAttribute("aria-busy", "true");
  listStatus.className = "message";
  listStatus.textContent = "Ładowanie...";
  listStatus.hidden = false;
}

export function showListError(message) {
  taskList.removeAttribute("aria-busy");
  listStatus.className = "message message-error";
  listStatus.textContent = message;
  listStatus.hidden = false;
}

export function hideListStatus() {
  taskList.removeAttribute("aria-busy");
  listStatus.hidden = true;
}

export function showFormError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

export function hideFormError() {
  formError.hidden = true;
}
