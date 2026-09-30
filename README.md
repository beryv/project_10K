# KBC Pulse AI Demo

A Nuxt and FastAPI demonstration backed by MariaDB, with a bundled JSON fallback. It loads the seeded KBC client profiles, financial summaries, transactions, payments, loans, insurances, investments, and AI nudges from `backend/kbc_pulse.sql`. All financial content is fictional and all recommendation actions are for demonstration only.

## Start the database and API

From the project root:

```powershell
docker compose -f backend/docker-compose.yml up --build -d
```

MariaDB initializes `backend/kbc_pulse.sql` when its data volume is first created. The script drops and recreates its KBC tables, so it is only mounted as an initialization script; Docker will not rerun it on an existing `mariadb_data` volume. The compose file uses development-only default credentials. Override `MARIADB_ROOT_PASSWORD` and `MARIADB_PASSWORD` for non-local environments.

The API falls back to `backend/clients_db.json` when MariaDB is unavailable. The frontend also bundles `frontend/data/clients_db.json`, so the profile selector, dashboard, local nudges, and chat remain demonstrable if the API container is offline. Local fallback nudge changes are not persisted across restarts.

To enable Gemini chat responses, set `GEMINI_API_KEY` in the environment or in `backend/.env` before starting Compose. `GEMINI_MODEL` can override the default `gemini-2.0-flash-lite`. If no key is configured or Gemini is unreachable, `classifier.py` returns deterministic, client-contextual responses. Nudge classification always has a deterministic transaction-trigger fallback.

The API and OpenAPI docs are available at `http://localhost:8000` and `http://localhost:8000/docs`. Check the DB connection at `http://localhost:8000/health`.

## Start the frontend

```powershell
docker compose -f frontend/docker-compose.yml up --build -d
```

Open `http://localhost:3000`. The root route sends you to the demo profile selector. Select one of the clients seeded in MariaDB to open the dashboard.

## API

- `GET /pulse/clients`: list available demo profiles.
- `GET /pulse/clients/{client_id}/dashboard`: load that client's financial profile and related records.
- `GET /pulse/clients/{client_id}/nudges`: list recommendations.
- `PATCH /pulse/clients/{client_id}/nudges/{nudge_id}`: persist a recommendation as `ACCEPTED` or `DISMISSED`.
- `GET /v1/clients` and `GET /v1/clients/{client_id}/dashboard`: versioned profile and dashboard routes.
- `GET /v1/clients/{client_id}/nudges`: recompute and return explainable nudges through `classifier.predict_nudges`.
- `POST /chat` (also `/v1/chat`): accept `{ "client_id": "kbc_user_2894", "message": "..." }` and call `classifier.generate_chatbot_response` with that client's complete context.

The dashboard header can switch profiles without a page reload; dashboard and nudge data refresh for the selected client and the chat history resets.

The SQL schema intentionally contains no passwords or credential table. The profile selector is a demo-only client switch, not real authentication. Add a proper identity provider and authorization checks before exposing any client data beyond a local demo. Do not use real personal, account, or payment information.
