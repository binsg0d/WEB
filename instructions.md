# Laboratorium 3 — instrukcja

## Frontend TaskBoard połączony z API

---

## Agenda

1. Przygotowanie: szkielet frontendu, trzy terminale, DevTools
2. Strona z dysku i strona z serwera
3. DOM: lista zadań z danych lokalnych
4. Formularz bez przeładowania strony
5. Pierwszy `fetch` i pierwszy błąd CORS
6. Konfiguracja CORS w FastAPI
7. POST i preflight
8. Obsługa błędów
9. Stan ładowania
10. Zadania samodzielne
11. Checkpoint

---

## 1. Cel

Do tej pory jedynym klientem twojego API był `curl`. Dziś TaskBoard dostaje klienta w przeglądarce: stronę, która pobiera listę zadań z API i tworzy nowe zadania bez przeładowania.

Po drodze trafisz na kilka błędów. Są zaplanowane. Każdy z nich wynika z mechanizmu omówionego na wykładzie 3 i każdy naprawisz dopiero wtedy, gdy zrozumiesz jego przyczynę. Najważniejsze narzędzie dzisiejszych zajęć to DevTools, a w nim zakładki **Console** i **Network**.

---

## 2. Co będzie gotowe na końcu

Strona `http://127.0.0.1:5500`, która:

- pobiera listę zadań z `http://127.0.0.1:8000/tasks` i renderuje ją przez DOM,
- dodaje zadanie przez formularz, wysyłając `POST /tasks` z ciałem JSON,
- usuwa zadanie przyciskiem przy każdej pozycji,
- filtruje listę po statusie,
- pokazuje komunikat ładowania i blokuje przycisk podczas wysyłania,
- pokazuje czytelny komunikat, gdy serwer odrzuci żądanie albo gdy serwer nie działa.

Backend dostaje `CORSMiddleware` z jawnie podanym origin frontendu.

Struktura projektu po zajęciach:

```text
taskboard/
├── app/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── api.js
│       ├── ui.js
│       └── main.js
├── pyproject.toml
├── uv.lock
└── README.md
```

### Podział plików JavaScript

| Plik | Odpowiedzialność |
|---|---|
| `api.js` | komunikacja z API, nie wie nic o DOM |
| `ui.js` | operacje na DOM, nie wie nic o HTTP |
| `main.js` | łączy oba: obsługuje zdarzenia i decyduje, co wywołać |

Ten podział jest celowo prosty. Przemyślaną architekturą frontendu (stan aplikacji, rendering jako funkcja stanu) zajmiemy się na zajęciach 7.

### Czego dziś świadomie nie ma

| Czego nie ma | Kiedy się pojawi |
|---|---|
| edycji zadań w interfejsie | zajęcia 4 i 7 |
| komunikatu „brak zadań" i przemyślanego modelu stanu | zajęcia 7 |
| adresów API i origin w konfiguracji zamiast w kodzie | zajęcia 5 i 13 |
| odrzucania pustego tytułu przez serwer | zajęcia 4 |
| logowania i cookies | zajęcia 8 |

---

## 3. Wymagania

- ukończone laboratorium 2, katalog `~/projects/taskboard` z działającym API,
- wykład 3,
- przeglądarka Firefox, Chromium albo Chrome.

Endpointy z laboratorium 2, z których dziś korzystamy:

| Metoda | Ścieżka | Status |
|---|---|---|
| GET | `/tasks` | 200 |
| POST | `/tasks` | 201, 409, 422 |
| DELETE | `/tasks/{task_id}` | 204, 404 |

Status 409 dla duplikatu tytułu pochodzi z zadania samodzielnego 1 laboratorium 2. Jeżeli go nie masz, dopisz go teraz albo skopiuj `app/main.py` ze `starter/`. Bez niego krok 8 nie będzie miał czego pokazać.

Nie znasz JavaScript? Wystarczy znajomość zmiennych, funkcji, obiektów i tablic na poziomie dowolnego kursu programowania. Składnia, której nie znasz z innych języków, jest wyjaśniona przy pierwszym użyciu.

---

## 4. Krok 0 — przygotowanie

### Szkielet frontendu

Skopiuj katalog `frontend/` ze `starter/` tego laboratorium do swojego projektu:

```bash
cp -R /sciezka/do/kursu/labs/03-frontend-fetch/starter/frontend ~/projects/taskboard/
cd ~/projects/taskboard
ls frontend frontend/js
```

```text
index.html  js  styles.css
main.js
```

`index.html` i `styles.css` są gotowe. Przejrzyj `index.html` i zwróć uwagę na:

- atrybuty `id` elementów, z których będziesz korzystać: `task-form`, `task-list`, `list-status`, `form-error`, `status-filter`, `reload-button`, `total`,
- pustą listę `<ul id="task-list">`,
- tag `<script type="module" src="js/main.js">` w sekcji `head`.

Zacommituj stan wyjściowy:

```bash
git add frontend
git commit -m "Szkielet frontendu"
```

### Trzy terminale

Przez całe zajęcia będą działały dwa serwery. Przygotuj trzy okna terminala, wszystkie w katalogu `~/projects/taskboard`:

| Terminal | Zawartość |
|---|---|
| 1 | serwer API: `uv run fastapi dev app/main.py` |
| 2 | serwer plików frontendu, krok 1 |
| 3 | polecenia `curl` i `git` |

Uruchom API w terminalu 1, jeżeli jeszcze nie działa.

### DevTools

Otwórz DevTools (`F12`). W zakładce Network zaznacz **Disable cache**. Opcja działa tylko wtedy, gdy DevTools są otwarte, więc nie zamykaj ich do końca zajęć.

Dlaczego: przeglądarka potrafi użyć zapamiętanej kopii pliku JS i nie zobaczysz swoich zmian. Wyjaśnienie tego zachowania to zajęcia 10.

---

## 5. Krok 1 — strona z dysku i strona z serwera

### Cel

Sprawdzić, czy przeglądarka może po prostu otworzyć plik z dysku.

### Działanie

Otwórz w przeglądarce plik bezpośrednio, na przykład przez menu Plik -> Otwórz albo wpisując w pasek adresu:

```text
file:///home/student/projects/taskboard/frontend/index.html
```

Strona się wyświetli, ale z konsoli zniknął komunikat z `main.js`. Zamiast niego jest błąd. W Chromium:

```text
Access to script at 'file:///.../frontend/js/main.js' from origin 'null' has been blocked
by CORS policy: Cross origin requests are only supported for protocol schemes:
chrome, chrome-untrusted, data, http, https.
```

Firefox zgłosi błąd z przyczyną „CORS request not HTTP".

### Wyjaśnienie

Skrypty `type="module"` są pobierane w trybie CORS. Plik z dysku ma origin `null`, a CORS działa wyłącznie dla schematów `http` i `https`. Moduł się nie załaduje.

Potrzebny jest serwer HTTP. Na pliki statyczne wystarczy serwer wbudowany w Pythona.

### Serwer plików

W terminalu 2:

```bash
uv run python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

```text
Serving HTTP on 127.0.0.1 port 5500 (http://127.0.0.1:5500/) ...
```

Otwórz `http://127.0.0.1:5500`. Zawsze używaj adresu `127.0.0.1`, a nie `localhost`. Dlaczego, zobaczysz w kroku 5.

`uv run python` uruchamia Pythona z projektu, więc działa niezależnie od tego, jaka wersja jest w systemie.

### Sprawdzenie

W konsoli:

```text
TaskBoard: main.js załadowany
```

W zakładce Network odśwież stronę. Widać trzy żądania: dokument, `styles.css` i `main.js`. Kliknij `main.js` i sprawdź nagłówek odpowiedzi `Content-Type: text/javascript`. Przeglądarka uruchomi moduł tylko wtedy, gdy serwer zadeklaruje go jako JavaScript.

### Checkpoint 1

Strona pod `http://127.0.0.1:5500` pokazuje nagłówek TaskBoard, a w konsoli jest komunikat z `main.js`.

---

## 6. Krok 2 — DOM: lista zadań z danych lokalnych

### Cel

Wyrenderować listę zadań przez DOM. Na razie z tablicy w kodzie, bez API. Najpierw chcemy mieć pewność, że renderowanie działa, a dopiero potem dokładać sieć.

### Moduł `ui.js`

Utwórz plik `frontend/js/ui.js`:

```js
const taskList = document.querySelector("#task-list");

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

  item.append(title, priority);
  return item;
}

export function renderTasks(tasks) {
  taskList.replaceChildren(...tasks.map(createTaskItem));
}
```

Co tu się dzieje:

| Fragment | Znaczenie |
|---|---|
| `document.querySelector("#task-list")` | znajduje element o `id="task-list"` |
| `document.createElement("li")` | tworzy nowy element, jeszcze niepodpięty do dokumentu |
| `item.dataset.id = task.id` | ustawia atrybut `data-id`, przyda się przy usuwaniu |
| `classList.add("task-done")` | wygląd zadania ukończonego definiuje CSS, JavaScript zmienia tylko klasę |
| `` `badge badge-${task.priority}` `` | template literal, odpowiednik f-stringa z Pythona |
| `textContent` | wstawia tekst dosłownie, bez interpretowania go jako HTML |
| `replaceChildren(...)` | usuwa dotychczasową zawartość listy i wstawia nowe elementy |
| `...tasks.map(...)` | `map` tworzy tablicę elementów, `...` rozkłada ją na osobne argumenty |
| `export` | funkcja jest widoczna dla innych modułów, `createTaskItem` nie jest |

Zwróć uwagę, że `querySelector` wykonuje się na najwyższym poziomie modułu, a skrypt jest dołączony w `<head>`, przed listą. Działa, bo moduły wykonują się dopiero po sparsowaniu całego dokumentu.

### Moduł `main.js`

Zastąp zawartość `frontend/js/main.js`:

```js
import { renderTasks } from "./ui.js";

const tasks = [
  { id: 1, title: "Zadanie lokalne", status: "open", priority: "high" },
  { id: 2, title: "Drugie zadanie lokalne", status: "done", priority: "low" },
];

renderTasks(tasks);
```

Ścieżka w `import` zaczyna się od `./` i zawiera rozszerzenie `.js`. Przeglądarka nie zgaduje rozszerzeń.

### Sprawdzenie

Odśwież stronę. Na liście są dwa zadania, drugie przekreślone.

W Network pojawiło się nowe żądanie: `ui.js`. Przeglądarka pobrała je, bo `main.js` je importuje. Każdy moduł to osobne żądanie HTTP.

Porównaj dwa widoki tej samej strony:

1. źródło strony (`Ctrl+U`): lista `<ul id="task-list">` jest pusta,
2. zakładka Elements (Inspector w Firefoksie): lista ma dwa elementy `li`.

Źródło pokazuje plik, który przyszedł z serwera. Elements pokazuje bieżący stan DOM.

Sprawdź też izolację modułów. Wpisz w konsoli:

```js
tasks
```

```text
Uncaught ReferenceError: tasks is not defined
```

Zmienna `tasks` istnieje wyłącznie w zakresie modułu `main.js`. Klasyczny skrypt umieściłby ją w zakresie globalnym.

---

## 7. Krok 3 — formularz bez przeładowania strony

### Cel

Dodawać zadanie z formularza. Najpierw zobaczysz, co formularz robi domyślnie.

### Etap A — bez obsługi zdarzenia

Wpisz tytuł i kliknij „Dodaj". Obserwuj pasek adresu i zakładkę Network.

Adres zmienił się na:

```text
http://127.0.0.1:5500/?title=Test&priority=medium
```

W Network pojawiło się nowe żądanie dokumentu. Strona przeładowała się i lista wróciła do stanu początkowego.

Formularz bez atrybutów `action` i `method` wysyła GET na bieżący adres z danymi w query stringu. To jest domyślne zachowanie przeglądarki: wysłanie formularza oznacza nawigację.

### Etap B — obsługa zdarzenia `submit`

Dopisz do `main.js`, pod wywołaniem `renderTasks(tasks)`:

```js
const form = document.querySelector("#task-form");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(form);
  tasks.push({
    id: tasks.length + 1,
    title: data.get("title"),
    status: "open",
    priority: data.get("priority"),
  });
  renderTasks(tasks);
  form.reset();
});
```

| Fragment | Znaczenie |
|---|---|
| `addEventListener("submit", ...)` | rejestruje funkcję wywoływaną przy wysłaniu formularza |
| `(event) => { ... }` | funkcja strzałkowa, odpowiednik `lambda`, ale może mieć wiele instrukcji |
| `event.preventDefault()` | anuluje domyślne zachowanie, czyli nawigację |
| `new FormData(form)` | odczytuje wartości pól po atrybutach `name` |
| `form.reset()` | czyści formularz |

Dlaczego `submit`, a nie `click` na przycisku: formularz można wysłać klawiszem Enter w polu tekstowym. `submit` obejmuje każdy sposób wysłania.

### Sprawdzenie

Dodaj dwa zadania. Pojawiają się na liście, adres się nie zmienia, w Network nie ma nowego żądania dokumentu.

Spróbuj wysłać formularz z pustym tytułem. Przeglądarka nie pozwoli, ponieważ pole ma atrybut `required`. Jest to walidacja po stronie przeglądarki. Zapamiętaj ją, wrócimy do niej w zadaniu samodzielnym 5.

Teraz odśwież stronę. Dodane zadania zniknęły.

### Wniosek

Stan trzymany w zmiennej JavaScript żyje tak długo jak dokument. Każde przeładowanie zaczyna od zera, a inna karta czy inny użytkownik nigdy tych zadań nie zobaczą. Dane muszą trafić tam, gdzie żyją dłużej niż karta przeglądarki. Mamy takie miejsce: API z laboratorium 2.

### Checkpoint 2

Formularz dodaje zadanie do listy bez przeładowania strony.

---

## 8. Krok 4 — pierwszy fetch i pierwszy błąd CORS

### Cel

Zastąpić dane lokalne danymi z API.

### Moduł `api.js`

Utwórz plik `frontend/js/api.js`:

```js
const API_URL = "http://127.0.0.1:8000";

export async function fetchTasks() {
  const response = await fetch(`${API_URL}/tasks`);
  const data = await response.json();
  return data.items;
}
```

| Fragment | Znaczenie |
|---|---|
| `async function` | funkcja asynchroniczna, zawsze zwraca Promise |
| `await fetch(...)` | wysyła żądanie i zawiesza funkcję do nadejścia nagłówków odpowiedzi |
| `await response.json()` | czeka na całe ciało i parsuje JSON |
| `data.items` | pole z odpowiedzi `{"items": [...], "total": 3}` z laboratorium 2 |

Dwa `await`, bo odpowiedź przychodzi w dwóch etapach: najpierw status i nagłówki, potem ciało, które może jeszcze płynąć przez sieć.

### Nowy `main.js`

Zastąp całą zawartość `main.js`:

```js
import { fetchTasks } from "./api.js";
import { renderTasks } from "./ui.js";

async function loadTasks() {
  const tasks = await fetchTasks();
  renderTasks(tasks);
}

loadTasks();
```

Formularz tymczasowo nie jest obsługiwany. Wróci w kroku 6, już połączony z API.

### Sprawdzenie

Odśwież stronę. Lista jest pusta. W konsoli dwa komunikaty. W Chromium:

```text
Access to fetch at 'http://127.0.0.1:8000/tasks' from origin 'http://127.0.0.1:5500'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
on the requested resource.

Uncaught (in promise) TypeError: Failed to fetch
```

W Firefoksie komunikat ma inną treść, ale tę samą przyczynę: brak nagłówka `Access-Control-Allow-Origin`.

### Diagnoza

Zanim cokolwiek naprawisz, zbierz trzy fakty.

**Fakt 1, Console.** Przeglądarka zgłasza błąd CORS.

**Fakt 2, Network.** Znajdź żądanie `tasks`. Jaki ma status?

W Firefoksie kolumna Status pokazuje 200, a przy żądaniu jest oznaczenie błędu CORS. W Chromium kolumna Status pokazuje „CORS error", co nie jest statusem HTTP, tylko werdyktem przeglądarki. Odpowiedź serwera rozstrzyga trzeci fakt.

**Fakt 3, log serwera.** Spójrz na terminal 1:

```text
INFO:     127.0.0.1:56584 - "GET /tasks HTTP/1.1" 200 OK
```

Serwer obsłużył żądanie i odpowiedział.

### Wyjaśnienie

Strona ma origin `http://127.0.0.1:5500`, API ma origin `http://127.0.0.1:8000`. Port jest inny, więc są to różne origin.

Same-Origin Policy nie zabroniła wysłania żądania. Zabroniła skryptowi **odczytać odpowiedź**, ponieważ serwer nie zadeklarował, że origin `http://127.0.0.1:5500` może ją czytać.

Sprawdź, co widzi serwer. W terminalu 3 wyślij to samo żądanie, łącznie z nagłówkiem `Origin`, który dodała przeglądarka:

```bash
curl -i -H "Origin: http://127.0.0.1:5500" http://127.0.0.1:8000/tasks
```

```http
HTTP/1.1 200 OK
content-type: application/json
x-total-count: 3

{"items":[...],"total":3}
```

`curl` dostaje dane bez przeszkód. Nie stosuje Same-Origin Policy. W odpowiedzi brakuje nagłówka `access-control-allow-origin` i to jego brak zatrzymał przeglądarkę.

Zwróć też uwagę na `Uncaught (in promise)`. Promise zwrócony przez `fetch` został odrzucony, a nikt nie obsłużył tego błędu. Zajmiemy się tym w kroku 7.

---

## 9. Krok 5 — konfiguracja CORS w FastAPI

### Cel

Serwer ma zadeklarować, że origin frontendu może czytać jego odpowiedzi.

### Kod

W `app/main.py` dopisz import:

```python
from fastapi.middleware.cors import CORSMiddleware
```

Bezpośrednio pod `app = FastAPI(title="TaskBoard")`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
)
```

Middleware to warstwa, przez którą przechodzi każde żądanie, zanim dotrze do endpointu, i każda odpowiedź, zanim wróci do klienta. `CORSMiddleware` dopisuje do odpowiedzi nagłówki CORS. Mechanizm middleware omówimy na zajęciach 5.

Origin podajemy jawnie. Nie używaj `["*"]`. Gwiazdka zezwala dowolnej stronie w internecie czytać odpowiedzi twojego API, a na zajęciach 8, gdy pojawią się cookies, przestanie działać.

### Sprawdzenie

Serwer w trybie `dev` przeładował się sam. Odśwież stronę. Lista zawiera trzy zadania z API.

W Network kliknij żądanie `tasks`. W nagłówkach odpowiedzi:

```http
access-control-allow-origin: http://127.0.0.1:5500
vary: Origin
```

Przeglądarka porównała nagłówek `Origin` żądania z `access-control-allow-origin` odpowiedzi, uznała je za zgodne i oddała odpowiedź skryptowi.

`vary: Origin` informuje pośrednie cache, że odpowiedź zależy od nagłówka `Origin`. Zajęcia 10.

### Eksperyment: `localhost` to nie `127.0.0.1`

Otwórz w nowej karcie `http://localhost:5500`. Strona się wyświetli, ale lista jest pusta, a w konsoli:

```text
Access to fetch at 'http://127.0.0.1:8000/tasks' from origin 'http://localhost:5500'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
on the requested resource.
```

`localhost` i `127.0.0.1` wskazują ten sam komputer, ale przeglądarka porównuje napisy, a nie adresy IP. Dla niej to dwa różne origin. Serwer zezwolił tylko na jeden.

Zamknij kartę z `localhost` i wróć do `127.0.0.1`.

### Checkpoint 3

Lista na stronie pokazuje zadania z API. W odpowiedzi `GET /tasks` widać nagłówek `access-control-allow-origin: http://127.0.0.1:5500`.

---

## 10. Krok 6 — POST i preflight

### Cel

Formularz ma tworzyć zadanie w API.

### Kod w `api.js`

Dopisz funkcję:

```js
export async function createTask(task) {
  const response = await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  return response.json();
}
```

Porównaj z poleceniem `curl` z laboratorium 2:

```text
curl -X POST                              -> method: "POST"
-H "Content-Type: application/json"       -> headers: {...}
-d '{"title":"..."}'                      -> body: JSON.stringify(task)
```

`JSON.stringify` zamienia obiekt JavaScript na tekst JSON. Bez niego `fetch` wysłałby napis `[object Object]`.

### Kod w `main.js`

Uzupełnij import i dopisz obsługę formularza pod funkcją `loadTasks`:

```js
import { createTask, fetchTasks } from "./api.js";
```

```js
const form = document.querySelector("#task-form");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  await createTask({
    title: data.get("title"),
    priority: data.get("priority"),
  });
  form.reset();
  await loadTasks();
});
```

Handler jest funkcją `async`, więc może czekać na odpowiedź serwera. Po utworzeniu zadania pobieramy listę od nowa. Źródłem prawdy jest serwer, a nie zmienna w przeglądarce.

`preventDefault()` musi być wywołane przed pierwszym `await`. Gdyby było po nim, przeglądarka wykonałaby domyślną nawigację, zanim funkcja wróciłaby do tej linii.

### Sprawdzenie

Dodaj zadanie przez formularz. Nie pojawia się na liście. W konsoli, w Chromium:

```text
Access to fetch at 'http://127.0.0.1:8000/tasks' from origin 'http://127.0.0.1:5500'
has been blocked by CORS policy: Response to preflight request doesn't pass access
control check: It does not have HTTP ok status.
```

### Diagnoza

W Network są tym razem dwa wpisy dotyczące `tasks`, w tym żądanie metodą **OPTIONS**. Kliknij je. W nagłówkach żądania:

```http
OPTIONS /tasks HTTP/1.1
Origin: http://127.0.0.1:5500
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type
```

Odpowiedź ma status 400. W logu serwera:

```text
INFO:     127.0.0.1:56596 - "OPTIONS /tasks HTTP/1.1" 400 Bad Request
```

I nic więcej. **Żądania POST w logu nie ma.** Sprawdź listę zadań przez `curl`: nowego zadania nie ma.

### Wyjaśnienie

POST z `Content-Type: application/json` nie jest simple request. Przed wysłaniem takiego żądania przeglądarka pyta serwer o zgodę żądaniem OPTIONS, czyli **preflight**: „czy origin `http://127.0.0.1:5500` może wysłać POST z nagłówkiem `content-type`?".

`CORSMiddleware` domyślnie zezwala wyłącznie na metodę GET. Na pytanie o POST odpowiedział odmową, więc przeglądarka nie wysłała właściwego żądania.

Odtwórz pytanie przeglądarki ręcznie:

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/tasks \
  -H "Origin: http://127.0.0.1:5500" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

```http
HTTP/1.1 400 Bad Request
access-control-allow-methods: GET
access-control-allow-origin: http://127.0.0.1:5500

Disallowed CORS method
```

Na wykładzie 2 widziałeś, że OPTIONS na twoim serwerze zwracał 405. Teraz wiesz, kto w praktyce wysyła OPTIONS: przeglądarka, przed każdym żądaniem, które nie jest simple request.

### Poprawka

W `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["GET", "POST"],
)
```

Nagłówka `Content-Type` nie trzeba dopisywać. Starlette zawsze zezwala na `Accept`, `Accept-Language`, `Content-Language` i `Content-Type`.

### Sprawdzenie

Dodaj zadanie przez formularz. Pojawia się na liście. W Network para żądań:

| Metoda | Status |
|---|---|
| OPTIONS | 200 |
| POST | 201 |

Po kolejnym dodaniu zadania preflight może się nie pojawić. Odpowiedź na preflight zawiera `access-control-max-age: 600`, więc przeglądarka zapamiętuje zgodę na pewien czas.

### Checkpoint 4

Formularz tworzy zadanie w API. W Network widać `OPTIONS /tasks` ze statusem 200 i `POST /tasks` ze statusem 201.

---

## 11. Krok 7 — obsługa błędów

### Cel

Użytkownik ma się dowiedzieć, że coś poszło nie tak. Najpierw sprawdzimy, co dzieje się teraz.

### Eksperyment 1 — duplikat tytułu

Dodaj zadanie o tytule, który już jest na liście, na przykład „Zaprojektować API".

Formularz się wyczyścił, lista się odświeżyła, nie ma żadnego komunikatu ani wyjątku w konsoli. Wygląda to na sukces. Ale nowego zadania na liście nie ma. W Network:

```text
POST /tasks  409
```

Serwer odrzucił żądanie, a kod zachował się tak, jakby wszystko było w porządku: wyczyścił formularz i odświeżył listę. Użytkownik ma prawo myśleć, że zadanie zostało dodane.

### Wyjaśnienie

`fetch` odrzuca Promise wyłącznie wtedy, gdy nie dostanie odpowiedzi. Odpowiedź 409 jest poprawnie zakończoną komunikacją: serwer odpowiedział. Interpretacja statusu należy do aplikacji.

| Sytuacja | Zachowanie `fetch` |
|---|---|
| 2xx | Promise spełniony, `response.ok === true` |
| 4xx, 5xx | Promise **spełniony**, `response.ok === false` |
| brak połączenia, odrzucenie przez CORS | Promise **odrzucony**, `TypeError` |

### Eksperyment 2 — zatrzymany serwer

Zatrzymaj serwer API w terminalu 1 (`Ctrl+C`) i odśwież stronę. W konsoli:

```text
Uncaught (in promise) TypeError: Failed to fetch
```

W Network żądanie zakończone błędem połączenia, bez statusu. Lista jest pusta i nic nie mówi, dlaczego.

Uruchom serwer ponownie.

### Kod w `api.js`

Wprowadzamy wspólną funkcję `request`, która sprawdza status każdej odpowiedzi, oraz własny typ błędu. Zastąp całą zawartość `api.js`:

```js
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
```

| Fragment | Znaczenie |
|---|---|
| `class ApiError extends Error` | błąd niosący status HTTP, odróżnialny od błędu sieci |
| `if (!response.ok)` | zamienia odpowiedź 4xx i 5xx na wyjątek |
| `response.json().catch(() => null)` | ciało błędu może nie być JSON-em, wtedy `null` |
| `body?.detail` | optional chaining: `undefined`, gdy `body` jest `null`, zamiast wyjątku |
| `typeof ... === "string"` | 409 i 404 mają `detail` jako tekst, 422 jako listę błędów |

Od tej chwili każda funkcja w `api.js` ma jedną z dwóch odpowiedzi: zwraca dane albo rzuca wyjątek. Kod korzystający z `api.js` nie musi pamiętać o `response.ok`.

Format pola `detail` jest częścią kontraktu API. Na zajęciach 4 zmienimy format błędów i ta funkcja będzie wymagała dostosowania. Tak wygląda w praktyce zależność klienta od kontraktu.

### Kod w `ui.js`

Na górze pliku dopisz odwołania do elementów komunikatów:

```js
const listStatus = document.querySelector("#list-status");
const formError = document.querySelector("#form-error");
```

Na końcu pliku dopisz funkcje:

```js
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
```

Atrybut `aria-busy` przyda się w kroku 8. Już teraz go usuwamy, żeby lista nie została w stanie ładowania po błędzie.

### Kod w `main.js`

Zastąp całą zawartość `main.js`:

```js
import { ApiError, createTask, fetchTasks } from "./api.js";
import {
  hideFormError,
  hideListStatus,
  renderTasks,
  showFormError,
  showListError,
} from "./ui.js";

const form = document.querySelector("#task-form");
const reloadButton = document.querySelector("#reload-button");

function describeError(error) {
  if (error instanceof ApiError) {
    return `Serwer odrzucił żądanie (${error.status}): ${error.message}`;
  }
  return "Brak połączenia z API. Sprawdź, czy serwer działa.";
}

async function loadTasks() {
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
  try {
    await createTask({
      title: data.get("title"),
      priority: data.get("priority"),
    });
    form.reset();
    await loadTasks();
  } catch (error) {
    showFormError(describeError(error));
  }
});

reloadButton.addEventListener("click", loadTasks);

loadTasks();
```

`describeError` rozróżnia dwa rodzaje porażki:

| Błąd | Kto zawinił | Komunikat |
|---|---|---|
| `ApiError` | serwer odpowiedział odmową | status i treść z serwera |
| każdy inny, w praktyce `TypeError` | brak odpowiedzi | brak połączenia |

Nie rozpoznajemy błędu po treści komunikatu. Chromium pisze „Failed to fetch", Safari „Load failed", Firefox jeszcze inaczej. Typ błędu jest jednakowy.

Zwróć uwagę, że błąd CORS również trafi do drugiej gałęzi. JavaScript nie może odróżnić odrzucenia przez CORS od braku sieci. Jest to celowe: gdyby mógł, skrypt z dowolnej strony mógłby sprawdzać, jakie serwery działają w sieci lokalnej użytkownika. Przyczynę błędu CORS zobaczysz tylko w konsoli DevTools.

### Sprawdzenie

1. Dodaj duplikat tytułu. Pod formularzem:

   ```text
   Serwer odrzucił żądanie (409): Zadanie o tym tytule już istnieje
   ```

2. Zatrzymaj serwer API i kliknij „Odśwież". Nad listą:

   ```text
   Brak połączenia z API. Sprawdź, czy serwer działa.
   ```

3. Uruchom serwer i kliknij „Odśwież". Komunikat znika, lista wraca.

W konsoli przy 409 nadal widać wpis „Failed to load resource: the server responded with a status of 409". To nie jest błąd twojego kodu. Przeglądarka loguje każdą odpowiedź 4xx i 5xx.

### Checkpoint 5

Duplikat tytułu wyświetla komunikat z treścią błędu 409. Zatrzymany serwer wyświetla komunikat o braku połączenia.

---

## 12. Krok 8 — stan ładowania

### Cel

Użytkownik ma widzieć, że coś się dzieje, i nie może wysłać formularza drugi raz, zanim przyjdzie odpowiedź.

### Problem

Lokalnie API odpowiada w kilka milisekund i stanu ładowania nie da się zobaczyć. Spowolnij sieć: w zakładce Network rozwiń listę throttlingu (domyślnie „No throttling") i wybierz najwolniejszy profil, na przykład „3G" w Chromium albo „Regular 3G" w Firefoksie. Nazwy profili zmieniają się między wersjami przeglądarek. Dodaj zadanie i obserwuj.

Przez kilka sekund nic się nie dzieje. Użytkownik nie wie, czy kliknięcie zadziałało, więc klika drugi raz. Drugi POST z tym samym tytułem dostanie 409. Bez reguły unikalności powstałyby dwa zadania. Wykład 2: POST nie jest idempotentny.

### Kod w `ui.js`

Dopisz funkcję:

```js
export function showListLoading() {
  taskList.setAttribute("aria-busy", "true");
  listStatus.className = "message";
  listStatus.textContent = "Ładowanie...";
  listStatus.hidden = false;
}
```

`aria-busy="true"` informuje technologie asystujące, że zawartość się zmienia. Plik CSS wykorzystuje ten sam atrybut do wyszarzenia listy. Jeden atrybut obsługuje dostępność i wygląd.

### Kod w `main.js`

Dopisz `showListLoading` do importu z `ui.js` oraz odwołanie do przycisku:

```js
const submitButton = document.querySelector("#submit-button");
```

Na początku `loadTasks`:

```js
async function loadTasks() {
  showListLoading();
  try {
```

W obsłudze formularza zablokuj przycisk na czas wysyłania:

```js
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
```

Blok `finally` wykona się zawsze: po sukcesie i po błędzie. Bez niego przycisk zostałby zablokowany na stałe po pierwszym błędzie.

### Sprawdzenie

Z włączonym throttlingiem:

1. odśwież stronę: przez chwilę widać „Ładowanie...",
2. dodaj zadanie: przycisk „Dodaj" jest wyszarzony do czasu odpowiedzi.

Po zakończeniu eksperymentu przywróć „No throttling".

---

## 13. Zadania samodzielne

### Zadanie 1 — usuwanie zadania

Przy każdym zadaniu ma być przycisk „Usuń", który wysyła `DELETE /tasks/{id}` i odświeża listę.

**Część A, `ui.js`.** W `createTaskItem` utwórz przycisk i dołącz go do elementu listy:

```js
const deleteButton = document.createElement("button");
deleteButton.type = "button";
deleteButton.className = "task-delete";
deleteButton.dataset.action = "delete";
deleteButton.textContent = "Usuń";

item.append(title, priority, deleteButton);
```

`type = "button"` jest potrzebne, żeby przycisk nie zachowywał się jak przycisk wysyłający formularz. Tutaj nie jest w formularzu, ale to dobry nawyk.

**Część B, `api.js`.** Napisz funkcję `deleteTask(taskId)` korzystającą z `request`. Odpowiedź 204 nie ma ciała, więc nie wywołuj `response.json()`.

**Część C, `main.js`.** Zamiast rejestrować handler na każdym przycisku, zarejestruj **jeden** handler na liście:

```js
const taskList = document.querySelector("#task-list");

taskList.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action='delete']");
  if (button === null) {
    return;
  }
  const taskId = button.closest(".task").dataset.id;
});
```

Uzupełnij handler: zablokuj przycisk, wywołaj `deleteTask`, odśwież listę, a przy błędzie pokaż komunikat przez `showListError` i odblokuj przycisk.

To jest event delegation. Kliknięcie przycisku propaguje się w górę drzewa do listy. `event.target` to faktycznie kliknięty element, `closest` szuka najbliższego przodka pasującego do selektora. Handler przypięty do listy przetrwa każde `replaceChildren`. Handlery przypięte do przycisków zginęłyby razem z nimi przy każdym odświeżeniu.

**Część D.** Kliknij „Usuń". Co pokazuje konsola i Network? Dlaczego? Popraw konfigurację CORS. Przy okazji dopisz także `PUT`, ponieważ API go obsługuje, a interfejs skorzysta z niego na zajęciach 7.

Sprawdzenie: w Network para `OPTIONS /tasks/4` 200 i `DELETE /tasks/4` 204, zadanie znika z listy.

### Zadanie 2 — filtr statusu

W `index.html` jest już pole `<select id="status-filter">`. Po zmianie jego wartości lista ma się odświeżyć z parametrem `status`.

1. Funkcja `fetchTasks(status)` przyjmuje opcjonalny argument.
2. Parametry zapytania zbuduj przez `URLSearchParams`, a nie przez sklejanie napisów:

   ```js
   const params = new URLSearchParams();
   if (status) {
     params.set("status", status);
   }
   const query = params.toString();
   const response = await request(query ? `/tasks?${query}` : "/tasks");
   ```

3. W `main.js` zarejestruj handler zdarzenia `change` na polu filtra i przekaż jego wartość do `fetchTasks`.

`URLSearchParams` koduje znaki specjalne. Spróbuj w konsoli:

```js
new URLSearchParams({ title: "a&b=c" }).toString()
```

```text
'title=a%26b%3Dc'
```

Sklejanie napisów dałoby `title=a&b=c`, czyli dwa parametry zamiast jednego.

Sprawdzenie: wybór „done" zostawia jedno zadanie, w Network widać `GET /tasks?status=done`.

### Zadanie 3 — liczba zadań z nagłówka

Pod listą jest element `<p id="total">`. Ma pokazywać tekst „Pasujących zadań: N", gdzie N pochodzi z nagłówka `X-Total-Count`, który API wysyła od laboratorium 2.

1. Zmień `fetchTasks`, żeby zwracała obiekt z listą i wartością nagłówka:

   ```js
   return {
     items: data.items,
     totalHeader: response.headers.get("X-Total-Count"),
   };
   ```

2. Dopisz w `ui.js` funkcję `renderTotal(totalHeader)`, która ustawi tekst elementu `#total`, a dla `null` wyczyści go.
3. Dostosuj `loadTasks`.

Uruchom. Nagłówek `x-total-count` jest widoczny w Network, a mimo to element pozostaje pusty. Sprawdź w konsoli, co zwraca `response.headers.get("X-Total-Count")`.

Domyślnie skrypt widzi w odpowiedzi cross-origin tylko kilka podstawowych nagłówków, takich jak `Content-Type`. Pozostałe serwer musi jawnie udostępnić. Znajdź w dokumentacji FastAPI parametr `CORSMiddleware`, który to robi, i dopisz go.

Sprawdzenie: pod listą „Pasujących zadań: 3", a po filtrze „done" „Pasujących zadań: 1". W nagłówkach odpowiedzi `access-control-expose-headers: X-Total-Count`.

### Zadanie 4 — kto egzekwuje CORS

Wyślij przez `curl` preflight z origin, którego nie ma na liście:

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/tasks \
  -H "Origin: http://evil.example" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Serwer odpowiada 400 `Disallowed CORS origin`. Teraz wyślij właściwy POST z tym samym origin, bez pytania o zgodę:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Origin: http://evil.example" \
  -H "Content-Type: application/json" \
  -d '{"title":"Z pominieciem preflight"}'
```

Odpowiedz na pytania:

1. Jaki status otrzymałeś za drugim razem? Czy zadanie powstało?
2. Kto w tej komunikacji egzekwuje CORS: serwer czy klient?
3. Czy konfiguracja `allow_origins` chroni twoje API przed nieuprawnionym dostępem? Kogo w takim razie chroni?

Prawdziwą ochronę dostępu, czyli authentication i authorization, dodamy na zajęciach 8 i 9.

### Zadanie 5 — dwie walidacje i jeden niebezpieczny tytuł

**Część A.** W DevTools, w zakładce Elements, usuń z pola tytułu atrybut `required` (dwuklik na atrybucie, potem usuń). Wyślij formularz z pustym tytułem.

Zadanie o pustym tytule powstało. Walidacja w przeglądarce jest wygodą dla użytkownika, a nie zabezpieczeniem. Każdy może ją ominąć, a `curl` nawet o niej nie wie. Model `TaskIn` wymaga pola `title`, ale akceptuje pusty napis. Regułę na długość tytułu dodamy po stronie serwera na zajęciach 4.

**Część B.** Dodaj zadanie o tytule:

```text
<b>pogrubiony</b>
```

Tytuł wyświetla się dosłownie, razem ze znacznikami. Zastanów się, co by się stało, gdyby `createTaskItem` używało `title.innerHTML` zamiast `title.textContent`. Możesz to sprawdzić na chwilę i przywrócić `textContent`. Zajęcia 9.

### Zadanie 6 — commit

```bash
git add .
git commit -m "Frontend TaskBoard: lista, formularz, usuwanie, CORS"
git log --oneline
```

---

## 14. Typowe problemy

### Problem 1 — zmiany w pliku JS nie są widoczne

**Przyczyna:** przeglądarka użyła zapamiętanej kopii pliku. `http.server` wysyła nagłówek `Last-Modified`, a przeglądarka może na jego podstawie przez pewien czas nie pytać serwera o plik.

**Rozwiązanie:** w Network zaznacz „Disable cache" i trzymaj DevTools otwarte. Doraźnie: `Ctrl+Shift+R`. Mechanizm wyjaśnimy na zajęciach 10.

### Problem 2 — `Uncaught SyntaxError: Cannot use import statement outside a module`

**Przyczyna:** brak `type="module"` w tagu `script`.

**Rozwiązanie:** nie zmieniaj `index.html` ze `starter/`. Tag ma postać `<script type="module" src="js/main.js">`.

### Problem 3 — `The requested module './ui.js' does not provide an export named 'renderTasks'`

**Przyczyna:** funkcja nie ma słowa `export` albo nazwa w `import` różni się od nazwy w module. Wielkość liter ma znaczenie.

**Rozwiązanie:** sprawdź `export function renderTasks` w `ui.js` i nawiasy klamrowe w `import`.

### Problem 4 — 404 na `ui.js` lub `api.js` w zakładce Network

**Przyczyna:** zła ścieżka w `import`. Częste warianty: brak `./`, brak rozszerzenia `.js`, plik w innym katalogu niż `js/`.

**Rozwiązanie:** ścieżka jest względna wobec pliku, który importuje. Z `js/main.js` poprawny zapis to `"./ui.js"`.

### Problem 5 — błąd CORS mimo poprawnej konfiguracji

**Lista kontrolna:**

1. Czy strona jest otwarta pod `http://127.0.0.1:5500`, a nie `http://localhost:5500`?
2. Czy origin w `allow_origins` nie ma ukośnika na końcu? `"http://127.0.0.1:5500/"` nie jest równe `"http://127.0.0.1:5500"`.
3. Czy serwer API przeładował się po zmianie? Sprawdź terminal 1, błąd składni zatrzymuje przeładowanie.
4. Czy błąd dotyczy preflight? Wtedy brakuje metody w `allow_methods`.

### Problem 6 — `TypeError: Failed to fetch` bez komunikatu CORS w konsoli

**Przyczyna:** serwer API nie działa albo działa pod innym portem. W Network żądanie ma status błędu połączenia, na przykład `net::ERR_CONNECTION_REFUSED`.

**Rozwiązanie:** sprawdź terminal 1 i adres w stałej `API_URL`.

### Problem 7 — `OSError: [Errno 98] Address already in use` przy uruchamianiu `http.server`

**Przyczyna:** port 5500 jest zajęty, na przykład przez serwer uruchomiony w innym terminalu albo rozszerzenie edytora typu Live Server.

**Rozwiązanie:**

```bash
ss -ltnp | grep 5500
```

Zatrzymaj proces, który zajmuje port. Nie zmieniaj portu bez potrzeby: origin `http://127.0.0.1:5500` jest wpisany w konfiguracji CORS.

### Problem 8 — strona przeładowuje się po kliknięciu „Dodaj"

**Przyczyna:** brak `event.preventDefault()`, wywołanie go po `await` albo błąd w handlerze, który przerwał jego wykonanie przed tą linią.

**Rozwiązanie:** `event.preventDefault()` musi być pierwszą instrukcją handlera. Jeżeli strona przeładowuje się mimo to, zaznacz w konsoli „Preserve log" (Firefox: „Persist Logs"), żeby zobaczyć błąd sprzed przeładowania.

### Problem 9 — lista pokazuje `undefined` albo nic, bez błędów w konsoli

**Przyczyna:** brak `await` przed `response.json()` albo przed wywołaniem funkcji `async`. Zmienna zawiera wtedy Promise, a nie dane.

**Rozwiązanie:** dodaj `console.log` zwracanej wartości. Jeżeli w konsoli widzisz `Promise {<pending>}`, brakuje `await`.

### Problem 10 — `422` przy dodawaniu zadania z przeglądarki

**Przyczyna:** brak nagłówka `Content-Type: application/json` albo ciało bez `JSON.stringify`.

**Rozwiązanie:** w Network kliknij żądanie POST i sprawdź zakładkę Payload (Firefox: Request). Ciało musi być poprawnym JSON-em, a nie tekstem `[object Object]`.

---

## 15. Checklista końcowa

- [ ] strona jest serwowana pod `http://127.0.0.1:5500`
- [ ] wiesz, dlaczego strona z modułami nie działa jako `file://`
- [ ] kod JavaScript jest podzielony na moduły `api.js`, `ui.js`, `main.js`
- [ ] lista zadań pochodzi z API i jest renderowana przez `createElement` i `textContent`
- [ ] potrafisz pokazać różnicę między źródłem strony a zakładką Elements
- [ ] formularz tworzy zadanie bez przeładowania strony
- [ ] potrafisz wskazać w logu serwera żądanie, którego odpowiedź zablokował CORS
- [ ] `CORSMiddleware` ma jawny origin, bez `*`
- [ ] w Network widać preflight `OPTIONS` przed `POST` i `DELETE`
- [ ] duplikat tytułu pokazuje komunikat z błędem 409
- [ ] zatrzymany serwer pokazuje komunikat o braku połączenia
- [ ] podczas wysyłania formularza przycisk jest zablokowany
- [ ] przycisk „Usuń" działa dzięki jednemu handlerowi na liście
- [ ] filtr statusu wysyła `GET /tasks?status=...`
- [ ] pod listą widać liczbę zadań z nagłówka `X-Total-Count`
- [ ] potrafisz wyjaśnić, kto egzekwuje CORS i kogo chroni
- [ ] zmiany są zacommitowane

---

## 16. Podsumowanie

Seria błędów, przez które przeszedłeś, i ich przyczyny:

```text
file://                -> moduł się nie ładuje       -> moduły wymagają HTTP
GET z innego origin    -> odpowiedź niedostępna      -> Access-Control-Allow-Origin
POST z JSON            -> POST nie wychodzi          -> preflight i allow_methods
409 z serwera          -> cisza                      -> fetch nie odrzuca 4xx, response.ok
zatrzymany serwer      -> TypeError                  -> Promise odrzucony bez odpowiedzi
X-Total-Count          -> null                       -> Access-Control-Expose-Headers
```

Najważniejsza obserwacja dzisiejszych zajęć: żądanie zablokowane przez CORS **dotarło do serwera** i zostało obsłużone. Przeglądarka zablokowała tylko odczyt odpowiedzi. CORS chroni użytkownika przeglądarki, nie twoje API.

### Stan projektu

| Element | Stan | Kiedy się zmieni |
|---|---|---|
| adres API w `api.js`, origin w `main.py` | wpisane w kod | zajęcia 5 i 13 |
| lista pobierana od nowa po każdej zmianie | proste i poprawne, ale kosztowne | zajęcia 7 |
| odczyt `detail` w `api.js` | zależny od obecnego formatu błędów | zajęcia 4 |
| brak edycji zadań | interfejs nie korzysta z PUT | zajęcia 7 |

### Na następne zajęcia

**Wykład 4** — projektowanie HTTP API i dane na granicy systemu: REST, zasoby, OpenAPI jako kontrakt, walidacja, spójny format błędów.

**Laboratorium 4** — API TaskBoard z zasobami `/projects` i `/users`, PATCH, osobnymi modelami wejścia i wyjścia oraz jednolitym formatem błędów. Dzisiejszy frontend będzie musiał przetrwać tę zmianę.
