from datetime import datetime
from database import Base
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship


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
  role = Column(String)
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
  balance = Column(Numeric(12, 2), default=0.0)
  account_type = Column(String)
  client_id = Column(Integer, ForeignKey("clients.id"))
  client = relationship("Client", back_populates="accounts")
  transactions = relationship("Transaction", back_populates="account")
  virtual_cards = relationship("VirtualCard", back_populates="account")


class Transaction(Base):
  __tablename__ = "transactions"
  id = Column(Integer, primary_key=True, index=True)
  amount = Column(Float)
  transaction_type = Column(String)
  description = Column(String, default="")
  timestamp = Column(DateTime, default=datetime.utcnow)
  account_id = Column(Integer, ForeignKey("accounts.id"))
  account = relationship("Account", back_populates="transactions")


class VirtualCard(Base):
  __tablename__ = "virtual_cards"
  id = Column(Integer, primary_key=True, index=True)
  card_reference = Column(String, unique=True, index=True)
  last_four = Column(String(4))
  card_type = Column(String)
  cardholder_name = Column(String)
  status = Column(String, default="Active")
  expiration_month = Column(Integer)
  expiration_year = Column(Integer)
  spending_limit = Column(Numeric(12, 2), default=500.0)
  credit_limit = Column(Numeric(12, 2), default=0.0)
  outstanding_balance = Column(Numeric(12, 2), default=0.0)
  account_id = Column(Integer, ForeignKey("accounts.id"))
  created_at = Column(DateTime, default=datetime.utcnow)
  account = relationship("Account", back_populates="virtual_cards")
  transactions = relationship("CardTransaction", back_populates="card")


class CardTransaction(Base):
  __tablename__ = "card_transactions"
  id = Column(Integer, primary_key=True, index=True)
  amount = Column(Numeric(12, 2))
  transaction_type = Column(String)
  merchant = Column(String)
  timestamp = Column(DateTime, default=datetime.utcnow)
  card_id = Column(Integer, ForeignKey("virtual_cards.id"))
  card = relationship("VirtualCard", back_populates="transactions")