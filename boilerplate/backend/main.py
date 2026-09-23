from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# SQLite database file path inside the container
SQLALCHEMY_DATABASE_URL = "sqlite:///./bank.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- DATABASE MODELS ---


class Branch(Base):
  __tablename__ = "branches"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=True, index=True)
  city = Column(String)

  employees = relationship("Employee", back_populates="branch")


class Employee(Base):
  __tablename__ = "employees"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)
  role = Column(String)  # e.g., Teller, Manager
  branch_id = Column(Integer, ForeignKey("branches.id"))

  branch = relationship("Branch", back_populates="employees")


class Client(Base):
  __tablename__ = "clients"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)
  email = Column(String, unique=True, index=True)

  accounts = relationship("Account", back_populates="client")


class Account(Base):
  __tablename__ = "accounts"
  id = Column(Integer, primary_key=True, index=True)
  account_number = Column(String, unique=True, index=True)
  balance = Column(Float, default=0.0)
  account_type = Column(String)  # Savings, Checking
  client_id = Column(Integer, ForeignKey("clients.id"))

  client = relationship("Client", back_populates="accounts")
  transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
  __tablename__ = "transactions"
  id = Column(Integer, primary_key=True, index=True)
  amount = Column(Float)
  transaction_type = Column(String)  # Deposit, Withdrawal
  timestamp = Column(DateTime, default=datetime.utcnow)
  account_id = Column(Integer, ForeignKey("accounts.id"))

  account = relationship("Account", back_populates="transactions")


# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Simulation API")


# --- PYDANTIC SCHEMAS ---


class BranchCreate(BaseModel):
  name: str
  city: str


class ClientCreate(BaseModel):
  name: str
  email: str


class AccountCreate(BaseModel):
  account_number: str
  account_type: str
  client_id: int
  initial_deposit: float = 0.0


class TransactionCreate(BaseModel):
  account_id: int
  amount: float
  transaction_type: str  # "Deposit" or "Withdrawal"


# --- DEPENDENCY ---


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


# --- API ENDPOINTS ---


@app.get("/")
def read_root():
  return {"message": "Welcome to the Bank Simulation API!"}


@app.post("/branches/")
def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
  db_branch = Branch(name=branch.name, city=branch.city)
  db.add(db_branch)
  db.commit()
  db.refresh(db_branch)
  return db_branch


@app.post("/clients/")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
  db_client = Client(name=client.name, email=client.email)
  db.add(db_client)
  db.commit()
  db.refresh(db_client)
  return db_client


@app.post("/accounts/")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
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


@app.post("/transactions/")
def make_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
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


@app.get("/accounts/{account_id}")
def get_account_details(account_id: int, db: Session = Depends(get_db)):
  account = db.query(Account).filter(Account.id == account_id).first()
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")
  return account