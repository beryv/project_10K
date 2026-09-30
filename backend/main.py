import os
from datetime import datetime, timedelta

from auth import (
    create_access_token,
    get_current_admin,
    oauth2_scheme,
    revoke_token,
    validate_token,
    verify_password,
)
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from models import Account, AdminUser, Branch, Client, Transaction
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System Dashboard"])
def health_check():
  return {"status": "ok"}


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
            <span class="badge">Status: Operational</span>
            <p>Your modular FastAPI microservice is successfully running with secure configuration and input validation.</p>
            <h3>Quick Links</h3>
            <ul>
                <li><strong>Interactive API Documentation:</strong> <a href="/docs" target="_blank">Swagger UI (/docs)</a></li>
                <li><strong>Health Check:</strong> <a href="/health" target="_blank">/health</a></li>
            </ul>
            <a href="/docs" class="btn">Open API Explorer</a>
        </div>
    </body>
    </html>
    """


@app.post("/token", tags=["Authentication"])
@app.post("/login", tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
  admin_user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
  if admin_user is None or not verify_password(form_data.password, admin_user.password_hash):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect admin username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = create_access_token(form_data.username)
  return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout", tags=["Authentication"])
@app.post("/logout/", tags=["Authentication"])
def logout_admin(token: str = Depends(oauth2_scheme)):
  """Invalidates the current bearer token for this session."""
  username = validate_token(token, allow_revoked=True)
  revoke_token(token)
  return {
      "message": "Logout successful",
      "detail": "Token revoked and cleared from client storage.",
      "logged_out_user": username,
  }


@app.get("/branches/", tags=["Public Data Views"])
def get_branches(db: Session = Depends(get_db)):
  return db.query(Branch).all()


@app.get("/clients/", tags=["Public Data Views"])
def get_clients(db: Session = Depends(get_db)):
  return db.query(Client).all()


@app.get("/accounts/", tags=["Public Data Views"])
def get_accounts(db: Session = Depends(get_db)):
  return db.query(Account).all()


@app.get("/transactions/", tags=["Public Data Views"])
def get_transactions(db: Session = Depends(get_db)):
  return db.query(Transaction).all()


@app.post("/addbranches/", tags=["Admin Management (Protected)"])
def add_branch(
    branch: BranchCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
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
  client_exists = db.query(Client).filter(Client.id == account.client_id).first()
  if not client_exists:
    raise HTTPException(status_code=404, detail="Client not found")

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
  account = db.query(Account).filter(Account.id == tx.account_id).first()
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")

  tx_type = tx.transaction_type.lower()
  if tx_type == "withdrawal":
    if account.balance < tx.amount:
      raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance -= tx.amount
  elif tx_type == "deposit":
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
  db.refresh(db_tx)

  return {
      "message": "Transaction successful",
      "new_balance": account.balance,
      "transaction_id": db_tx.id,
  }