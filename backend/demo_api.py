from decimal import Decimal
from datetime import datetime
import secrets
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Request
from main import app, accrue_month_end_interest, validate_annual_rate
from database import Base, SessionLocal, engine, get_db
from models import (
  Account,
  CardTransaction,
  Client,
  ClientDebt,
  ClientRequest,
  DebtTransaction,
  Transaction,
  VirtualCard,
)
from schemas import (
  DemoAccountCreate,
  DemoCardControlsUpdate,
  DemoCardCreate,
  DemoCardPayment,
  DemoCardPurchase,
  DemoCardStatusUpdate,
  DemoDebtCreate,
  DemoDebtPayment,
  DemoDeposit,
  DemoPayment,
  DemoTransfer,
)
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)
transaction_columns = {
    column["name"] for column in inspect(engine).get_columns("transactions")
}
if "description" not in transaction_columns:
  with engine.begin() as connection:
    connection.execute(
        text("ALTER TABLE transactions ADD COLUMN description VARCHAR DEFAULT ''")
    )

demo_router = APIRouter(tags=["Demo Banking"])
card_router = APIRouter(tags=["Virtual Cards"])
liability_router = APIRouter(tags=["Debts"])


def describe_request(method: str, path: str):
  fixed_actions = {
      ("GET", "/demo/dashboard"): "view_dashboard",
      ("POST", "/demo/accounts"): "create_account",
      ("POST", "/demo/deposits"): "receive_money",
      ("POST", "/demo/payments"): "send_payment",
      ("POST", "/demo/transfers"): "transfer_between_accounts",
      ("POST", "/demo/cards"): "create_virtual_card",
        ("POST", "/demo/debts"): "record_debt",
  }
  if (method, path) in fixed_actions:
    return fixed_actions[(method, path)]
  if method == "POST" and path.startswith("/demo/accounts/") and path.endswith("/close"):
    return "close_account"
  if method == "POST" and path.startswith("/demo/debts/") and path.endswith("/payments"):
    return "pay_debt"
  if path.endswith("/details"):
    return "view_card_details"
  if path.endswith("/status"):
    return "change_card_status"
  if path.endswith("/controls"):
    return "change_card_controls"
  if path.endswith("/purchases"):
    return "card_purchase"
  if path.endswith("/payments"):
    return "pay_credit_card"
  return f"{method} {path}"[:160]


@app.middleware("http")
async def log_client_request(request: Request, call_next):
  started_at = perf_counter()
  status_code = 500
  try:
    response = await call_next(request)
    status_code = response.status_code
    return response
  finally:
    path = request.url.path.replace("\r", "").replace("\n", "")[:512]
    method = request.method[:12]
    action = describe_request(method, path)
    duration_ms = int((perf_counter() - started_at) * 1000)
    db = SessionLocal()
    client_id = None
    try:
      client = db.query(Client).order_by(Client.id).first()
      client_id = client.id if client else None
      db.add(
          ClientRequest(
              client_id=client_id,
              method=method,
              path=path,
              action=action,
              status_code=status_code,
              duration_ms=duration_ms,
          )
      )
      db.commit()
    except Exception as error:
      db.rollback()
      print(f"[CLIENT_REQUEST_AUDIT_ERROR] {type(error).__name__}", flush=True)
    finally:
      db.close()
    print(
        f"[CLIENT_REQUEST] client_id={client_id or '-'} action={action!r} "
        f"method={method} status={status_code} duration_ms={duration_ms}",
        flush=True,
    )


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


def get_demo_card(db: Session, client_id: int, card_id: int):
  card = (
      db.query(VirtualCard)
      .join(Account, VirtualCard.account_id == Account.id)
      .filter(VirtualCard.id == card_id, Account.client_id == client_id)
      .first()
  )
  if not card:
    raise HTTPException(status_code=404, detail="Virtual card not found")
  return card


@demo_router.get("/demo/dashboard")
def get_demo_dashboard(db: Session = Depends(get_db)):
  client = get_demo_client(db)
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
  return {
      "client": client,
      "accounts": accounts,
      "transactions": transactions,
      "cards": cards,
      "card_transactions": card_transactions,
  }


@demo_router.post("/demo/accounts")
def open_demo_account(payload: DemoAccountCreate, db: Session = Depends(get_db)):
  client = get_demo_client(db)
  account = Account(
      account_number=f"SIM-{secrets.token_hex(5).upper()}",
      balance=Decimal("0.00"),
      account_type=payload.account_type,
      client_id=client.id,
  )
  db.add(account)
  db.commit()
  db.refresh(account)
  return account


@demo_router.post("/demo/deposits")
def simulate_deposit(payload: DemoDeposit, db: Session = Depends(get_db)):
  validate_demo_amount(payload.amount)
  client = get_demo_client(db)
  account = get_demo_account(db, client.id, payload.account_id)
  account.balance = Decimal(str(account.balance)) + payload.amount
  db.add(
      Transaction(
          amount=payload.amount,
          transaction_type="Deposit",
          description="Simulated incoming payment",
          account_id=account.id,
      )
  )
  db.commit()
  return {"message": "Simulated deposit complete", "new_balance": account.balance}


@demo_router.post("/demo/payments")
def simulate_payment(payload: DemoPayment, db: Session = Depends(get_db)):
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


@demo_router.post("/demo/transfers")
def simulate_transfer(payload: DemoTransfer, db: Session = Depends(get_db)):
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


@card_router.post("/demo/cards")
def create_virtual_card(payload: DemoCardCreate, db: Session = Depends(get_db)):
  validate_demo_amount(payload.spending_limit)
  client = get_demo_client(db)
  account = get_demo_account(db, client.id, payload.account_id)
  credit_limit = Decimal("0.00")
  annual_interest_rate = Decimal("0.00")
  if payload.card_type == "Credit":
    validate_annual_rate(payload.annual_interest_rate)
    validate_demo_amount(payload.credit_limit)
    if payload.credit_limit < Decimal("100.00") or payload.credit_limit > Decimal("50000.00"):
      raise HTTPException(status_code=400, detail="Credit limit must be between 100 and 50,000")
    if payload.spending_limit > payload.credit_limit:
      raise HTTPException(status_code=400, detail="Purchase limit cannot exceed credit limit")
    credit_limit = payload.credit_limit
    annual_interest_rate = payload.annual_interest_rate
  now = datetime.utcnow()
  card = VirtualCard(
      card_reference=secrets.token_hex(16).upper(),
      last_four=f"{secrets.randbelow(10000):04d}",
      card_type=payload.card_type,
      cardholder_name=client.name,
      status="Active",
      expiration_month=now.month,
      expiration_year=now.year + 3,
      spending_limit=payload.spending_limit,
      credit_limit=credit_limit,
      outstanding_balance=Decimal("0.00"),
      annual_interest_rate=annual_interest_rate,
      account_id=account.id,
  )
  db.add(card)
  db.commit()
  db.refresh(card)
  return card


@card_router.get("/demo/cards/{card_id}/details")
def get_virtual_card_details(card_id: int, db: Session = Depends(get_db)):
  client = get_demo_client(db)
  card = get_demo_card(db, client.id, card_id)
  demo_digits = f"{int(card.card_reference, 16) % 100000000:08d}"
  return {
      "card_number": f"0000 {demo_digits[:4]} {demo_digits[4:]} {card.last_four}",
      "cardholder_name": card.cardholder_name,
      "expiration_month": card.expiration_month,
      "expiration_year": card.expiration_year,
      "security_code": "000",
      "status": card.status,
      "simulation_only": True,
  }


@card_router.patch("/demo/cards/{card_id}/status")
def update_virtual_card_status(
    card_id: int,
    payload: DemoCardStatusUpdate,
    db: Session = Depends(get_db),
):
  client = get_demo_client(db)
  card = get_demo_card(db, client.id, card_id)
  if card.status == "Closed" and payload.status != "Closed":
    raise HTTPException(status_code=409, detail="Closed cards cannot be reactivated")
  card.status = payload.status
  db.commit()
  return card


@card_router.patch("/demo/cards/{card_id}/controls")
def update_virtual_card_controls(
    card_id: int,
    payload: DemoCardControlsUpdate,
    db: Session = Depends(get_db),
):
  validate_demo_amount(payload.spending_limit)
  client = get_demo_client(db)
  card = get_demo_card(db, client.id, card_id)
  if card.status == "Closed":
    raise HTTPException(status_code=409, detail="Closed cards cannot be changed")
  if card.card_type == "Credit" and payload.spending_limit > Decimal(str(card.credit_limit)):
    raise HTTPException(status_code=400, detail="Purchase limit cannot exceed credit limit")
  card.spending_limit = payload.spending_limit
  db.commit()
  return card


@card_router.post("/demo/cards/{card_id}/purchases")
def simulate_card_purchase(
    card_id: int,
    payload: DemoCardPurchase,
    db: Session = Depends(get_db),
):
  validate_demo_amount(payload.amount)
  merchant = payload.merchant.strip()
  if not merchant or len(merchant) > 80:
    raise HTTPException(status_code=400, detail="Enter a merchant name")
  client = get_demo_client(db)
  accrue_month_end_interest(db, client.id)
  card = get_demo_card(db, client.id, card_id)
  if card.status != "Active":
    raise HTTPException(status_code=400, detail="This card is not active")
  if payload.amount > Decimal(str(card.spending_limit)):
    raise HTTPException(status_code=400, detail="Purchase exceeds the card spending limit")
  account = get_demo_account(db, client.id, card.account_id)
  if card.card_type == "Debit":
    balance = Decimal(str(account.balance))
    if balance < payload.amount:
      raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance = balance - payload.amount
    db.add(
        Transaction(
            amount=payload.amount,
            transaction_type="Card payment",
            description=f"Card purchase at {merchant} · •••• {card.last_four}",
            account_id=account.id,
        )
    )
  else:
    available_credit = Decimal(str(card.credit_limit)) - Decimal(str(card.outstanding_balance))
    if available_credit < payload.amount:
      raise HTTPException(status_code=400, detail="Insufficient available credit")
    card.outstanding_balance = Decimal(str(card.outstanding_balance)) + payload.amount
  db.add(
      CardTransaction(
          amount=payload.amount,
          transaction_type="Purchase",
          merchant=merchant,
          card_id=card.id,
      )
  )
  db.commit()
  return {
      "message": "Simulated card purchase complete",
      "account_balance": account.balance,
      "outstanding_balance": card.outstanding_balance,
  }


@card_router.post("/demo/cards/{card_id}/payments")
def pay_virtual_credit_card(
    card_id: int,
    payload: DemoCardPayment,
    db: Session = Depends(get_db),
):
  validate_demo_amount(payload.amount)
  client = get_demo_client(db)
  accrue_month_end_interest(db, client.id)
  card = get_demo_card(db, client.id, card_id)
  if card.card_type != "Credit":
    raise HTTPException(status_code=400, detail="Only credit cards have a bill to pay")
  outstanding = Decimal(str(card.outstanding_balance))
  if payload.amount > outstanding:
    raise HTTPException(status_code=400, detail="Payment exceeds the outstanding balance")
  account = get_demo_account(db, client.id, payload.account_id)
  balance = Decimal(str(account.balance))
  if balance < payload.amount:
    raise HTTPException(status_code=400, detail="Insufficient funds")
  account.balance = balance - payload.amount
  card.outstanding_balance = outstanding - payload.amount
  db.add_all([
      Transaction(
          amount=payload.amount,
          transaction_type="Card bill payment",
          description=f"Payment to virtual card · •••• {card.last_four}",
          account_id=account.id,
      ),
      CardTransaction(
          amount=payload.amount,
          transaction_type="Payment",
          merchant=f"Payment from {account.account_type.lower()} account",
          card_id=card.id,
      ),
  ])
  db.commit()
  return {
      "message": "Credit card payment complete",
      "account_balance": account.balance,
      "outstanding_balance": card.outstanding_balance,
  }


@liability_router.post("/demo/debts")
def create_demo_debt(payload: DemoDebtCreate, db: Session = Depends(get_db)):
  description = payload.description.strip()
  if not description or len(description) > 120:
    raise HTTPException(status_code=400, detail="Enter a debt name up to 120 characters")
  validate_demo_amount(payload.initial_balance)
  validate_annual_rate(payload.annual_interest_rate)
  client = get_demo_client(db)
  debt = ClientDebt(
      description=description,
      balance=payload.initial_balance,
      annual_interest_rate=payload.annual_interest_rate,
      status="Active",
      client_id=client.id,
  )
  db.add(debt)
  db.flush()
  db.add(
      DebtTransaction(
          amount=payload.initial_balance,
          transaction_type="Opened",
          description="Opening debt balance",
          debt_id=debt.id,
      )
  )
  db.commit()
  db.refresh(debt)
  return debt


@liability_router.post("/demo/debts/{debt_id}/payments")
def pay_demo_debt(
    debt_id: int,
    payload: DemoDebtPayment,
    db: Session = Depends(get_db),
):
  validate_demo_amount(payload.amount)
  client = get_demo_client(db)
  accrue_month_end_interest(db, client.id)
  debt = (
      db.query(ClientDebt)
      .filter(ClientDebt.id == debt_id, ClientDebt.client_id == client.id)
      .first()
  )
  if not debt:
    raise HTTPException(status_code=404, detail="Debt not found")
  if debt.status != "Active":
    raise HTTPException(status_code=409, detail="This debt is already paid")
  balance = Decimal(str(debt.balance))
  if payload.amount > balance:
    raise HTTPException(status_code=400, detail="Payment exceeds the outstanding debt")
  account = get_demo_account(db, client.id, payload.account_id)
  account_balance = Decimal(str(account.balance))
  if account_balance < payload.amount:
    raise HTTPException(status_code=400, detail="Insufficient funds")
  account.balance = account_balance - payload.amount
  debt.balance = balance - payload.amount
  if debt.balance == 0:
    debt.status = "Paid"
  db.add_all([
      Transaction(
          amount=payload.amount,
          transaction_type="Debt payment",
          description=f"Payment toward {debt.description}",
          account_id=account.id,
      ),
      DebtTransaction(
          amount=payload.amount,
          transaction_type="Payment",
          description=f"Payment from {account.account_type.lower()} account",
          debt_id=debt.id,
      ),
  ])
  db.commit()
  return {
      "message": "Debt payment complete",
      "account_balance": account.balance,
      "debt_balance": debt.balance,
      "debt_status": debt.status,
  }


registered_paths = {getattr(route, "path", None) for route in app.routes}
if "/demo/dashboard" not in registered_paths:
  app.include_router(demo_router)
if "/demo/cards" not in registered_paths:
  app.include_router(card_router)
if "/demo/debts" not in registered_paths:
  app.include_router(liability_router)
