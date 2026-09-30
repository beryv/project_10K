from datetime import date, datetime
from database import Base
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func


class Client(Base):
  __tablename__ = "clients"

  client_id = Column(String(36), primary_key=True)
  persona_type = Column(String(100), nullable=False)
  first_name = Column(String(50), nullable=False)
  last_name = Column(String(50), nullable=False)
  age = Column(Integer, nullable=False)
  civil_status = Column(String(50), nullable=False)
  profession = Column(String(100), nullable=False)
  monthly_net_income = Column(Numeric(10, 2), nullable=False)
  investor_profile = Column(String(50), nullable=False)
  kbc_segment = Column(String(100), nullable=False)
  ai_consent_active = Column(Boolean, default=True)
  created_at = Column(DateTime, server_default=func.current_timestamp())


class FinancialSummary(Base):
  __tablename__ = "financial_summaries"

  summary_id = Column(Integer, primary_key=True, autoincrement=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  total_available_capital = Column(Numeric(12, 2), nullable=False)
  liquid_cash = Column(Numeric(12, 2), nullable=False)
  savings_account = Column(Numeric(12, 2), nullable=False)
  investments_value = Column(Numeric(12, 2), nullable=False)
  total_monthly_deficits_or_debts = Column(Numeric(10, 2), nullable=False)
  net_worth_trend_30d = Column(String(20), nullable=False)


class Transaction(Base):
  __tablename__ = "transactions"

  transaction_id = Column(String(36), primary_key=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  tx_date = Column(Date, nullable=False)
  merchant = Column(String(100), nullable=False)
  category = Column(String(50), nullable=False)
  amount = Column(Numeric(10, 2), nullable=False)
  tx_type = Column(String(10), nullable=False)
  flag_ai_trigger = Column(String(100))


class UpcomingPayment(Base):
  __tablename__ = "upcoming_payments"

  payment_id = Column(Integer, primary_key=True, autoincrement=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  label = Column(String(100), nullable=False)
  amount = Column(Numeric(10, 2), nullable=False)
  due_date = Column(Date, nullable=False)
  status = Column(String(16), default="PLANNED")


class Loan(Base):
  __tablename__ = "loans"

  loan_id = Column(Integer, primary_key=True, autoincrement=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  loan_type = Column(String(100), nullable=False)
  initial_amount = Column(Numeric(12, 2), nullable=False)
  remaining_balance = Column(Numeric(12, 2), nullable=False, default=0)
  monthly_payment = Column(Numeric(10, 2), nullable=False, default=0)
  status = Column(String(20), nullable=False)
  start_date = Column(Date, nullable=False)
  end_date = Column(Date, nullable=False)


class Insurance(Base):
  __tablename__ = "insurances"

  insurance_id = Column(Integer, primary_key=True, autoincrement=True)
  contract_code = Column(String(50), unique=True, nullable=False)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  insurance_type = Column(String(100), nullable=False)
  monthly_premium = Column(Numeric(10, 2), nullable=False)
  status = Column(String(16), default="ACTIVE")
  start_date = Column(Date, nullable=False)
  end_date = Column(Date)


class Investment(Base):
  __tablename__ = "investments"

  investment_id = Column(Integer, primary_key=True, autoincrement=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  holding_name = Column(String(100), nullable=False)
  holding_type = Column(String(50), nullable=False)
  asset_value = Column(Numeric(12, 2), nullable=False)
  return_ytd = Column(String(20), nullable=False)


class AIPredictionNudge(Base):
  __tablename__ = "ai_predictions_nudges"

  nudge_id = Column(String(36), primary_key=True)
  client_id = Column(String(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
  priority = Column(String(10), nullable=False)
  category = Column(String(50), nullable=False)
  title = Column(String(150), nullable=False)
  description = Column(Text, nullable=False)
  explainability_reason = Column(Text, nullable=False)
  confidence_score = Column(Numeric(3, 2), nullable=False)
  status = Column(String(20), default="PENDING")
  created_at = Column(DateTime, server_default=func.current_timestamp())
