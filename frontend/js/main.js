import { ApiError, createTask, fetchTasks } from "./api.js";
import {
  hideFormError,
  hideListStatus,
  renderTasks,
  showFormError,
  showListError,
  showListLoading, // <-- Dodano brakujący import
} from "./ui.js";

const form = document.querySelector("#task-form");
const reloadButton = document.querySelector("#reload-button");
const submitButton = form.querySelector("button[type='submit']"); // <-- Dodano deklarację przycisku
function describeError(error) {
  if (error instanceof ApiError) {
    return `Serwer odrzucił żądanie (${error.status}): ${error.message}`;
  }
  return "Brak połączenia z API. Sprawdź, czy serwer działa.";
}
    
async function loadTasks() {
  showListLoading();
  try {
    const tasks = await fetchTasks();
    renderTasks(tasks);
    hideListStatus();
  } catch (error) {
    showListError(describeError(error));
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideFormError();
  const data = new FormData(form);
  submitButton.disabled = true;
  try {
    await createTask({
      title: data.get("title"),
      priority: data.get("priority"),
    });
    form.reset();
    await loadTasks();
  } catch (error) {
    showFormError(describeError(error));
  } finally {
    submitButton.disabled = false;
  }
});

reloadButton.addEventListener("click", loadTasks);

loadTasks();
