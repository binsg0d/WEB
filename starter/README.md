# TaskBoard

System zarzadzania projektami i zadaniami rozwijany na laboratoriach przedmiotu
Podstawy programowania aplikacji webowych.

## Uruchomienie

API:

```bash
uv sync
uv run fastapi dev app/main.py
```

Frontend, w drugim terminalu:

```bash
uv run python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

API: http://127.0.0.1:8000, frontend: http://127.0.0.1:5500

Frontend musi byc otwierany pod adresem `http://127.0.0.1:5500`. Ten origin jest
wpisany w konfiguracji CORS. Adres `http://localhost:5500` jest innym origin.

## Endpointy

| Metoda | Sciezka | Status | Opis |
|---|---|---|---|
| GET | `/` | 200 | odpowiedz powitalna |
| GET | `/health` | 200 | status aplikacji |
| GET | `/tasks` | 200 | lista zadan, parametry `status` oraz `limit` |
| GET | `/tasks/{task_id}` | 200, 404 | pojedyncze zadanie |
| POST | `/tasks` | 201, 409, 422 | utworzenie zadania |
| PUT | `/tasks/{task_id}` | 200, 404 | zastapienie zadania |
| DELETE | `/tasks/{task_id}` | 204, 404 | usuniecie zadania |
| GET | `/docs` | 200 | dokumentacja OpenAPI |

## Frontend

| Plik | Odpowiedzialnosc |
|---|---|
| `frontend/js/api.js` | komunikacja z API |
| `frontend/js/ui.js` | operacje na DOM |
| `frontend/js/main.js` | obsluga zdarzen, polaczenie obu modulow |

## Stan projektu

Po laboratorium 3: frontend w vanilla JavaScript pobiera, tworzy i usuwa zadania
przez Fetch API. Backend ma skonfigurowany CORS.

Dane sa przechowywane w pamieci procesu i znikaja po restarcie serwera.
Trwalosc danych zostanie dodana na zajeciach 6.
