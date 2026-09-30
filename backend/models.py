from datetime import datetime
from database import Base
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


class AdminUser(Base):
  __tablename__ = "admin_users"
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, index=True)
  password_hash = Column(String)


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
  balance = Column(Float, default=0.0)
  account_type = Column(String)
  client_id = Column(Integer, ForeignKey("clients.id"))
  client = relationship("Client", back_populates="accounts")
  transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
  __tablename__ = "transactions"
  id = Column(Integer, primary_key=True, index=True)
  amount = Column(Float)
  transaction_type = Column(String)
  timestamp = Column(DateTime, default=datetime.utcnow)
  account_id = Column(Integer, ForeignKey("accounts.id"))
  account = relationship("Account", back_populates="transactions")