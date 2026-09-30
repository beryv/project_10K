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
- Use each account’s options menu to copy its number or close it; closing transfers its remaining balance to another active account, and linked cards must be closed first.
- Simulate incoming deposits, payments to a named recipient, and transfers between owned accounts.
- Issue virtual debit and credit cards linked to an account, then freeze, unfreeze, or close them.
- Record personal debts with an APR and repay them from active accounts; liabilities reduce the displayed net balance.
- Set per-purchase limits and APRs, simulate credit-card purchases, and pay down card balances. Interest is compounded monthly at APR / 12 and posted once per completed billing month.
- Review balances and the persisted transaction ledger in the dashboard.
- Every HTTP request is recorded in the `client_requests` table and printed as `[CLIENT_REQUEST]` in the backend console, including reads and rejected requests.
- Amounts must be positive, limited to two decimal places, and cannot exceed available funds.

Card numbers are fictional and generated on demand from a random reference; the displayed number starts with `0000` and the security code is `000`. No full card number or security code is stored. All customer-facing routes use the first seeded client as a shared demo profile. Do not use real personal, account, or payment information. This project is a local simulation, not production banking software.

Request audit rows include the client, method, path, mapped action, response status, timestamp, and duration. Request bodies, query strings, and headers are not stored.