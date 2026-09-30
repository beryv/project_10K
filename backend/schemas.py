from decimal import Decimal
from typing import Literal
from pydantic import BaseModel


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
  transaction_type: str


class DemoAccountCreate(BaseModel):
  account_type: Literal["Current", "Savings"]


class DemoDeposit(BaseModel):
  account_id: int
  amount: Decimal


class DemoPayment(BaseModel):
  account_id: int
  amount: Decimal
  recipient: str


class DemoTransfer(BaseModel):
  source_account_id: int
  destination_account_id: int
  amount: Decimal


class DemoCardCreate(BaseModel):
  account_id: int
  card_type: Literal["Debit", "Credit"]
  spending_limit: Decimal = Decimal("500.00")
  credit_limit: Decimal = Decimal("1000.00")


class DemoCardStatusUpdate(BaseModel):
  status: Literal["Active", "Frozen", "Closed"]


class DemoCardControlsUpdate(BaseModel):
  spending_limit: Decimal


class DemoCardPurchase(BaseModel):
  amount: Decimal
  merchant: str


class DemoCardPayment(BaseModel):
  account_id: int
  amount: Decimal