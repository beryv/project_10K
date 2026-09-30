from pydantic import BaseModel, EmailStr, Field, validator


class BranchCreate(BaseModel):
  name: str = Field(..., min_length=2, max_length=100)
  city: str = Field(..., min_length=2, max_length=100)


class ClientCreate(BaseModel):
  name: str = Field(..., min_length=2, max_length=100)
  email: EmailStr


class AccountCreate(BaseModel):
  account_number: str = Field(..., min_length=4, max_length=32)
  account_type: str = Field(..., min_length=2, max_length=50)
  client_id: int = Field(..., gt=0)
  initial_deposit: float = Field(default=0.0, ge=0)


class TransactionCreate(BaseModel):
  account_id: int = Field(..., gt=0)
  amount: float = Field(..., gt=0)
  transaction_type: str = Field(..., min_length=3, max_length=20)

  @validator("transaction_type")
  def validate_transaction_type(cls, value):
    normalized = value.strip()
    if normalized.lower() not in {"deposit", "withdrawal"}:
      raise ValueError("transaction_type must be 'Deposit' or 'Withdrawal'")
    return normalized.title()