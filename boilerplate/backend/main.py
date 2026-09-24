from datetime import datetime, timedelta
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    ADMIN_PASSWORD_HASH,
    ADMIN_USERNAME,
    SECRET_KEY,
    get_current_admin,
    verify_password,
)
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from models import Account, Branch, Client, Transaction
from schemas import (
    AccountCreate,
    BranchCreate,
    ClientCreate,
    TransactionCreate,
)
from seed import seed_database
from sqlalchemy.orm import Session

# Initialize database & seeder
Base.metadata.create_all(bind=engine)
seed_database()

# Initialize FastAPI without default docs to use the custom polished view
app = FastAPI(
    title="Secure Core Banking API",
    description=(
        "A modular, fully documented simulation of a banking backend with"
        " polished UI."
    ),
    version="2.1.0",
    docs_url=None,
    redoc_url=None,
)


# --- CUSTOM POLISHED /docs UI ---
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
  return get_swagger_ui_html(
      openapi_url=app.openapi_url,
      title="Secure Core Banking API | Docs",
      oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
      swagger_js_url=(
          "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
      ),
      swagger_css_url=(
          "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
      ),
      swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
  )


# --- SYSTEM DASHBOARD / ROOT ROUTE ---
@app.get("/", response_class=HTMLResponse, tags=["System Dashboard"])
def read_root():
  return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Core Banking Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 40px; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
            h1 { color: #1a73e8; margin-top: 0; }
            .badge { background: #e8f0fe; color: #1a73e8; padding: 5px 10px; border-radius: 4px; font-size: 14px; font-weight: bold; }
            .btn { display: inline-block; background: #1a73e8; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; }
            .btn:hover { background: #1557b0; }
            ul { line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Secure Core Banking API</h1>
            <span class="badge">Status: Operational (Polished UI)</span>
            <p>Your modular FastAPI microservice is successfully running inside Docker with custom styled documentation.</p>
            <h3>Quick Links</h3>
            <ul>
                <li><strong>Interactive API Documentation:</strong> <a href="/docs" target="_blank">Swagger UI (/docs)</a></li>
            </ul>
            <a href="/docs" class="btn">Open API Explorer</a>
        </div>
    </body>
    </html>
    """


# --- ADMIN AUTHENTICATION ---
@app.post("/token", tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
  """Authenticate the admin user to receive a bearer token for writing data."""
  if form_data.username != ADMIN_USERNAME or not verify_password(
      form_data.password, ADMIN_PASSWORD_HASH
  ):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect admin username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = jwt.encode(
      {"sub": form_data.username, "exp": datetime.utcnow() + access_token_expires},
      SECRET_KEY,
      algorithm=ALGORITHM,
  )
  return {"access_token": access_token, "token_type": "bearer"}


# --- PUBLIC READ-ONLY GET ENDPOINTS ---
@app.get("/branches/", tags=["Public Data Views"])
def get_branches(db: Session = Depends(get_db)):
  """Retrieve a list of all registered bank branches."""
  return db.query(Branch).all()


@app.get("/clients/", tags=["Public Data Views"])
def get_clients(db: Session = Depends(get_db)):
  """Retrieve a list of all bank clients."""
  return db.query(Client).all()


@app.get("/accounts/", tags=["Public Data Views"])
def get_accounts(db: Session = Depends(get_db)):
  """Retrieve all client bank accounts and current balances."""
  return db.query(Account).all()


@app.get("/transactions/", tags=["Public Data Views"])
def get_transactions(db: Session = Depends(get_db)):
  """Retrieve a full history of all processed banking transactions."""
  return db.query(Transaction).all()


# --- SECURE ADMIN POST ENDPOINTS ---
@app.post("/addbranches/", tags=["Admin Management (Protected)"])
def add_branch(
    branch: BranchCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
  """Register a new bank branch (Admin token required)."""
  db_branch = Branch(name=branch.name, city=branch.city)
  db.add(db_branch)
  db.commit()
  db.refresh(db_branch)
  return db_branch


@app.post("/addclients/", tags=["Admin Management (Protected)"])
def add_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
  """Register a new bank client (Admin token required)."""
  db_client = Client(name=client.name, email=client.email)
  db.add(db_client)
  db.commit()
  db.refresh(db_client)
  return db_client


@app.post("/addaccounts/", tags=["Admin Management (Protected)"])
def add_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
  """Open a new bank account for a client (Admin token required)."""
  db_account = Account(
      account_number=account.account_number,
      account_type=account.account_type,
      client_id=account.client_id,
      balance=account.initial_deposit,
  )
  db.add(db_account)
  db.commit()
  db.refresh(db_account)
  return db_account


@app.post("/addtransactions/", tags=["Admin Management (Protected)"])
def add_transaction(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
  """Process a deposit or withdrawal on an account (Admin token required)."""
  account = db.query(Account).filter(Account.id == tx.account_id).first()
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")

  if tx.transaction_type == "Withdrawal":
    if account.balance < tx.amount:
      raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance -= tx.amount
  elif tx.transaction_type == "Deposit":
    account.balance += tx.amount
  else:
    raise HTTPException(status_code=400, detail="Invalid transaction type")

  db_tx = Transaction(
      amount=tx.amount,
      transaction_type=tx.transaction_type,
      account_id=tx.account_id,
  )
  db.add(db_tx)
  db.commit()

  return {
      "message": "Transaction successful",
      "new_balance": account.balance,
      "transaction_id": db_tx.id,
  }