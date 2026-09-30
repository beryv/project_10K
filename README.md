# KBC Pulse AI Demo

A Nuxt and FastAPI demonstration backed by MariaDB. It loads the seeded KBC client profiles, financial summaries, transactions, payments, loans, insurances, investments, and AI nudges from `backend/kbc_pulse.sql`. All financial content is fictional and all recommendation actions are for demonstration only.

## Start the database and API

From the project root:

```powershell
docker compose -f backend/docker-compose.yml up --build -d
```

MariaDB initializes `backend/kbc_pulse.sql` when its data volume is first created. The script drops and recreates its KBC tables, so it is only mounted as an initialization script; Docker will not rerun it on an existing `mariadb_data` volume. The compose file uses development-only default credentials. Override `MARIADB_ROOT_PASSWORD` and `MARIADB_PASSWORD` for non-local environments.

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

The SQL schema intentionally contains no passwords or credential table. The profile selector is a demo-only client switch, not real authentication. Add a proper identity provider and authorization checks before exposing any client data beyond a local demo. Do not use real personal, account, or payment information.
