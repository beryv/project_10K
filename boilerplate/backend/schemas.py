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