from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    ADMIN_PASSWORD_HASH,
    ADMIN_USERNAME,
    SECRET_KEY,
    get_current_admin,
    verify_password,
)
from database import get_db, initialize_database
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from models import (
    Account,
    Branch,
    CardTransaction,
    Client,
    ClientDebt,
    DebtTransaction,
    InterestAccrual,
    Transaction,
    VirtualCard,
)
from schemas import (
    AccountCreate,
    BranchCreate,
    ClientCreate,
    DemoAccountClose,
    DemoAccountCreate,
    DemoDebtCreate,
    DemoDebtPayment,
    DemoDeposit,
    DemoPayment,
    DemoTransfer,
    TransactionCreate,
)
from seed import seed_database
from sqlalchemy.orm import Session
import secrets

# Initialize database & seeder
initialize_database()
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


def get_demo_client(db: Session):
  client = db.query(Client).order_by(Client.id).first()
  if not client:
    raise HTTPException(status_code=404, detail="Demo customer not found")
  return client


def validate_demo_amount(amount: Decimal):
  if not amount.is_finite() or amount <= 0 or amount > Decimal("1000000.00"):
    raise HTTPException(status_code=400, detail="Enter an amount from 0.01 to 1,000,000")
  if amount.as_tuple().exponent < -2:
    raise HTTPException(status_code=400, detail="Amounts can have at most two decimal places")


def validate_annual_rate(rate: Decimal):
  if not rate.is_finite() or rate < 0 or rate > Decimal("100.00"):
    raise HTTPException(status_code=400, detail="Annual interest rate must be between 0 and 100 percent")
  if rate.as_tuple().exponent < -2:
    raise HTTPException(status_code=400, detail="Interest rates can have at most two decimal places")


def billing_periods(started_at: datetime, through: date):
  period = date(started_at.year, started_at.month, 1)
  last_period = date(through.year, through.month, 1)
  while period <= last_period:
    yield period.strftime("%Y-%m")
    if period.month == 12:
      period = date(period.year + 1, 1, 1)
    else:
      period = date(period.year, period.month + 1, 1)


def last_completed_billing_period(now: datetime):
  if now.month == 1:
    return date(now.year - 1, 12, 1)
  return date(now.year, now.month - 1, 1)


def accrue_month_end_interest(db: Session, client_id: int, now: datetime | None = None):
  now = now or datetime.utcnow()
  through_period = last_completed_billing_period(now)
  changed = False

  debts = (
    db.query(ClientDebt)
    .filter(ClientDebt.client_id == client_id, ClientDebt.status == "Active")
    .all()
  )
  for debt in debts:
    balance = Decimal(str(debt.balance))
    rate = Decimal(str(debt.annual_interest_rate))
    for period in billing_periods(debt.created_at, through_period):
      exists = (
        db.query(InterestAccrual.id)
        .filter_by(subject_type="Debt", subject_id=debt.id, billing_period=period)
        .first()
      )
      if exists:
        continue
      interest = (balance * rate / Decimal("1200")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
      )
      db.add(
        InterestAccrual(
          client_id=client_id,
          subject_type="Debt",
          subject_id=debt.id,
          billing_period=period,
          amount=interest,
        )
      )
      if interest > 0:
        balance += interest
        db.add(
          DebtTransaction(
            amount=interest,
            transaction_type="Interest",
            description=f"Monthly interest for {period}",
            debt_id=debt.id,
          )
        )
      changed = True
    debt.balance = balance

  cards = (
    db.query(VirtualCard)
    .join(Account, VirtualCard.account_id == Account.id)
    .filter(Account.client_id == client_id, VirtualCard.card_type == "Credit")
    .all()
  )
  for card in cards:
    balance = Decimal(str(card.outstanding_balance))
    rate = Decimal(str(card.annual_interest_rate))
    for period in billing_periods(card.created_at, through_period):
      exists = (
        db.query(InterestAccrual.id)
        .filter_by(subject_type="CreditCard", subject_id=card.id, billing_period=period)
        .first()
      )
      if exists:
        continue
      interest = (balance * rate / Decimal("1200")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
      )
      db.add(
        InterestAccrual(
          client_id=client_id,
          subject_type="CreditCard",
          subject_id=card.id,
          billing_period=period,
          amount=interest,
        )
      )
      if interest > 0:
        balance += interest
        db.add(
          CardTransaction(
            amount=interest,
            transaction_type="Interest",
            merchant=f"Monthly interest · {period}",
            card_id=card.id,
          )
        )
      changed = True
    card.outstanding_balance = balance

  if changed:
    db.commit()


def get_demo_account(db: Session, client_id: int, account_id: int):
  account = (
      db.query(Account)
      .filter(Account.id == account_id, Account.client_id == client_id)
      .first()
  )
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")
  if account.status != "Active":
    raise HTTPException(status_code=409, detail="Account is closed")
  return account


@app.get("/demo/dashboard", tags=["Demo Banking"])
def get_demo_dashboard(db: Session = Depends(get_db)):
  """Return the seeded demo customer's accounts and recent activity."""
  client = get_demo_client(db)
  accrue_month_end_interest(db, client.id)
  accounts = db.query(Account).filter(Account.client_id == client.id).all()
  account_ids = [account.id for account in accounts]
  transactions = (
      db.query(Transaction)
      .filter(Transaction.account_id.in_(account_ids))
      .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
      .limit(30)
      .all()
  ) if account_ids else []
  cards = (
      db.query(VirtualCard)
      .filter(VirtualCard.account_id.in_(account_ids))
      .order_by(VirtualCard.created_at.desc(), VirtualCard.id.desc())
      .all()
  ) if account_ids else []
  card_ids = [card.id for card in cards]
  card_transactions = (
      db.query(CardTransaction)
      .filter(CardTransaction.card_id.in_(card_ids))
      .order_by(CardTransaction.timestamp.desc(), CardTransaction.id.desc())
      .limit(20)
      .all()
  ) if card_ids else []
  debts = (
      db.query(ClientDebt)
      .filter(ClientDebt.client_id == client.id)
      .order_by(ClientDebt.created_at.desc(), ClientDebt.id.desc())
      .all()
  )
  debt_ids = [debt.id for debt in debts]
  debt_transactions = (
      db.query(DebtTransaction)
      .filter(DebtTransaction.debt_id.in_(debt_ids))
      .order_by(DebtTransaction.timestamp.desc(), DebtTransaction.id.desc())
      .limit(30)
      .all()
  ) if debt_ids else []
  return {
      "client": client,
      "accounts": accounts,
      "transactions": transactions,
      "cards": cards,
      "card_transactions": card_transactions,
      "debts": debts,
      "debt_transactions": debt_transactions,
  }


@app.post("/demo/accounts", tags=["Demo Banking"])
def open_demo_account(payload: DemoAccountCreate, db: Session = Depends(get_db)):
  """Open a current or savings account for the demo customer."""
  client = get_demo_client(db)
  account_number = f"SIM-{secrets.token_hex(5).upper()}"
  account = Account(
      account_number=account_number,
      balance=Decimal("0.00"),
      account_type=payload.account_type,
      client_id=client.id,
  )
  db.add(account)
  db.commit()
  db.refresh(account)
  return account


@app.post("/demo/accounts/{account_id}/close", tags=["Demo Banking"])
def close_demo_account(
    account_id: int,
    payload: DemoAccountClose,
    db: Session = Depends(get_db),
):
  client = get_demo_client(db)
  account = get_demo_account(db, client.id, account_id)
  if account_id == payload.destination_account_id:
    raise HTTPException(status_code=400, detail="Choose a different destination account")
  destination = get_demo_account(db, client.id, payload.destination_account_id)
  balance = Decimal(str(account.balance))
  if balance < 0:
    raise HTTPException(
        status_code=409,
        detail="An account with a negative balance cannot be closed",
    )
  linked_card = (
      db.query(VirtualCard)
      .filter(VirtualCard.account_id == account.id, VirtualCard.status != "Closed")
      .first()
  )
  if linked_card:
    raise HTTPException(
        status_code=409,
        detail="Close the virtual cards linked to this account first",
    )
  if balance > 0:
      destination.balance = Decimal(str(destination.balance)) + balance
      account.balance = Decimal("0.00")
      db.add_all([
          Transaction(
              amount=balance,
              transaction_type="Transfer out",
              description=f"Final balance transferred to {destination.account_type.lower()} account",
              account_id=account.id,
          ),
          Transaction(
              amount=balance,
              transaction_type="Transfer in",
              description=f"Final balance received from {account.account_type.lower()} account",
              account_id=destination.id,
          ),
      ])
  account.status = "Closed"
  db.commit()
  return {
      "message": "Account closed",
      "account_id": account.id,
      "destination_account_id": destination.id,
      "transferred_amount": balance,
      "status": account.status,
  }


@app.post("/demo/deposits", tags=["Demo Banking"])
def simulate_deposit(payload: DemoDeposit, db: Session = Depends(get_db)):
  """Simulate incoming money into one of the demo customer's accounts."""
  validate_demo_amount(payload.amount)
  client = get_demo_client(db)
  account = get_demo_account(db, client.id, payload.account_id)
  account.balance = Decimal(str(account.balance)) + payload.amount
  transaction = Transaction(
      amount=payload.amount,
      transaction_type="Deposit",
      description="Simulated incoming payment",
      account_id=account.id,
  )
  db.add(transaction)
  db.commit()
  return {"message": "Simulated deposit complete", "new_balance": account.balance}


@app.post("/demo/payments", tags=["Demo Banking"])
def simulate_payment(payload: DemoPayment, db: Session = Depends(get_db)):
  """Simulate a payment to an external recipient without moving real money."""
  validate_demo_amount(payload.amount)
  recipient = payload.recipient.strip()
  if not recipient or len(recipient) > 80:
    raise HTTPException(status_code=400, detail="Enter a recipient name")
  client = get_demo_client(db)
  account = get_demo_account(db, client.id, payload.account_id)
  balance = Decimal(str(account.balance))
  if balance < payload.amount:
    raise HTTPException(status_code=400, detail="Insufficient funds")
  account.balance = balance - payload.amount
  db.add(
      Transaction(
          amount=payload.amount,
          transaction_type="Payment",
          description=f"Payment to {recipient}",
          account_id=account.id,
      )
  )
  db.commit()
  return {"message": "Simulated payment complete", "new_balance": account.balance}


@app.post("/demo/transfers", tags=["Demo Banking"])
def simulate_transfer(payload: DemoTransfer, db: Session = Depends(get_db)):
  """Move simulated funds between the demo customer's own accounts."""
  validate_demo_amount(payload.amount)
  if payload.source_account_id == payload.destination_account_id:
    raise HTTPException(status_code=400, detail="Choose two different accounts")
  client = get_demo_client(db)
  source = get_demo_account(db, client.id, payload.source_account_id)
  destination = get_demo_account(db, client.id, payload.destination_account_id)
  source_balance = Decimal(str(source.balance))
  if source_balance < payload.amount:
    raise HTTPException(status_code=400, detail="Insufficient funds")
  source.balance = source_balance - payload.amount
  destination.balance = Decimal(str(destination.balance)) + payload.amount
  db.add_all([
      Transaction(
          amount=payload.amount,
          transaction_type="Transfer out",
          description=f"Transfer to {destination.account_type.lower()} account",
          account_id=source.id,
      ),
      Transaction(
          amount=payload.amount,
          transaction_type="Transfer in",
          description=f"Transfer from {source.account_type.lower()} account",
          account_id=destination.id,
      ),
  ])
  db.commit()
  return {"message": "Transfer complete", "new_balance": source.balance}


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