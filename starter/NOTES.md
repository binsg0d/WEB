# Stan początkowy laboratorium 4

Katalog jest kopią `labs/03-frontend-fetch/solution/` bez zmian: backend z `CORSMiddleware` i frontend z modułami `api.js`, `ui.js`, `main.js`.

## Kto czego potrzebuje

| Sytuacja | Co zrobić |
|---|---|
| własny projekt po laboratorium 3, z zadaniami samodzielnymi | nic, kontynuujesz własny projekt |
| własny projekt bez zadań samodzielnych | nic, brakujące metody w `allow_methods` dopiszesz w kroku 7 instrukcji |
| brak projektu | skopiuj cały katalog |

## Uruchomienie

Terminal 1:

```bash
uv sync
uv run fastapi dev app/main.py
```

Terminal 2:

```bash
uv run python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Przeglądarka: `http://127.0.0.1:5500`, API: `http://127.0.0.1:8000/docs`.
