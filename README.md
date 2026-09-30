# Aster Bank Simulator

A fictional banking sandbox built with FastAPI, SQLite, and Nuxt. Use it to explore current and savings accounts, incoming payments, outgoing payments, internal transfers, and account activity. It does not connect to a bank or move real money.

## Run locally

Start the backend from the `backend` directory:

```powershell
py -3 -m uvicorn demo_api:app --host 0.0.0.0 --reload --port 8000
```

Start the frontend from the `frontend` directory:

```powershell
npm install
npm run dev -- --host 0.0.0.0
```

Open `http://localhost:3000`. The backend API and interactive docs are available at `http://localhost:8000` and `http://localhost:8000/docs`.

## Demo workflows

- Open current or savings accounts for the seeded demo customer.
- Simulate incoming deposits, payments to a named recipient, and transfers between owned accounts.
- Issue virtual debit and credit cards linked to an account, then freeze, unfreeze, or close them.
- Set per-purchase limits, simulate card purchases, and pay down simulated credit balances.
- Review balances and the persisted transaction ledger in the dashboard.
- Amounts must be positive, limited to two decimal places, and cannot exceed available funds.

Card numbers are fictional and generated on demand from a random reference; the displayed number starts with `0000` and the security code is `000`. No full card number or security code is stored. All customer-facing routes use the first seeded client as a shared demo profile. Do not use real personal, account, or payment information. This project is a local simulation, not production banking software.