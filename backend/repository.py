import json
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any

from models import (
    AIPredictionNudge,
    Client,
    FinancialSummary,
    Insurance,
    Investment,
    Loan,
    Transaction,
    UpcomingPayment,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


_FALLBACK_PATH = Path(__file__).with_name("clients_db.json")
_FALLBACK_CLIENTS = json.loads(_FALLBACK_PATH.read_text(encoding="utf-8"))["clients"]
_FALLBACK_STATUS_UPDATES: dict[tuple[str, str], str] = {}


def _number(value: Any) -> float:
  return float(value or 0)


def _date(value: date | datetime | None) -> str | None:
  return value.isoformat() if value else None


def _serialize_client(client: Client) -> dict[str, Any]:
  return {
      "client_id": client.client_id,
      "first_name": client.first_name,
      "last_name": client.last_name,
      "display_name": f"{client.first_name} {client.last_name}",
      "age": client.age,
      "persona_type": client.persona_type,
      "civil_status": client.civil_status,
      "profession": client.profession,
      "monthly_net_income": _number(client.monthly_net_income),
      "investor_profile": client.investor_profile,
      "kbc_segment": client.kbc_segment,
      "ai_consent_active": bool(client.ai_consent_active),
  }


def _serialize_nudge(nudge: AIPredictionNudge) -> dict[str, Any]:
  return {
      "nudge_id": nudge.nudge_id,
      "priority": nudge.priority,
      "category": nudge.category,
      "title": nudge.title,
      "description": nudge.description,
      "explainability_reason": nudge.explainability_reason,
      "confidence_score": _number(nudge.confidence_score),
      "status": nudge.status,
      "created_at": _date(nudge.created_at),
  }


class ClientRepository:
  """Read a normalized client context from MariaDB, falling back to bundled JSON."""

  def __init__(self, db: Session):
    self.db = db
    self.source = "mariadb"

  def list_clients(self) -> list[dict[str, Any]]:
    try:
      clients = self.db.query(Client).order_by(Client.age.asc()).all()
      if clients:
        self.source = "mariadb"
        return [_serialize_client(client) for client in clients]
    except SQLAlchemyError:
      self.db.rollback()

    self.source = "json"
    return [deepcopy(item["client"]) for item in _FALLBACK_CLIENTS]

  def get_client_context(self, client_id: str) -> dict[str, Any] | None:
    try:
      client = self.db.query(Client).filter(Client.client_id == client_id).first()
      if client:
        self.source = "mariadb"
        return self._database_context(client)
    except SQLAlchemyError:
      self.db.rollback()

    fallback = next(
        (item for item in _FALLBACK_CLIENTS if item["client"]["client_id"] == client_id),
        None,
    )
    if fallback is None:
      return None
    self.source = "json"
    context = deepcopy(fallback)
    for nudge in context["nudges"]:
      nudge["status"] = _FALLBACK_STATUS_UPDATES.get(
          (client_id, nudge["nudge_id"]), nudge.get("status", "PENDING")
      )
    context["source"] = "json"
    return context

  def update_nudge_status(self, client_id: str, nudge_id: str, status: str) -> dict[str, Any] | None:
    try:
      nudge = (
          self.db.query(AIPredictionNudge)
          .filter(
              AIPredictionNudge.client_id == client_id,
              AIPredictionNudge.nudge_id == nudge_id,
          )
          .first()
      )
      if nudge:
        nudge.status = status
        self.db.commit()
        self.db.refresh(nudge)
        self.source = "mariadb"
        return _serialize_nudge(nudge)
    except SQLAlchemyError:
      self.db.rollback()

    context = self.get_client_context(client_id)
    if context is None:
      return None
    nudge = next((item for item in context["nudges"] if item["nudge_id"] == nudge_id), None)
    if nudge is None:
      return None
    _FALLBACK_STATUS_UPDATES[(client_id, nudge_id)] = status
    nudge["status"] = status
    self.source = "json"
    return nudge

  def _database_context(self, client: Client) -> dict[str, Any]:
    client_id = client.client_id
    summary = (
        self.db.query(FinancialSummary)
        .filter(FinancialSummary.client_id == client_id)
        .order_by(FinancialSummary.summary_id.desc())
        .first()
    )
    payments = (
        self.db.query(UpcomingPayment)
        .filter(
            UpcomingPayment.client_id == client_id,
            UpcomingPayment.status.in_(["PLANNED", "PROCESSING"]),
        )
        .order_by(UpcomingPayment.due_date.asc(), UpcomingPayment.payment_id.asc())
        .all()
    )
    investments = (
        self.db.query(Investment)
        .filter(Investment.client_id == client_id)
        .order_by(Investment.investment_id.asc())
        .all()
    )
    transactions = (
        self.db.query(Transaction)
        .filter(Transaction.client_id == client_id)
        .order_by(Transaction.tx_date.desc(), Transaction.transaction_id.desc())
        .all()
    )
    loans = (
        self.db.query(Loan)
        .filter(Loan.client_id == client_id)
        .order_by(Loan.loan_id.asc())
        .all()
    )
    insurances = (
        self.db.query(Insurance)
        .filter(Insurance.client_id == client_id)
        .order_by(Insurance.insurance_id.asc())
        .all()
    )
    nudges = (
        self.db.query(AIPredictionNudge)
        .filter(AIPredictionNudge.client_id == client_id)
        .order_by(AIPredictionNudge.created_at.asc(), AIPredictionNudge.nudge_id.asc())
        .all()
    )

    return {
        "client": _serialize_client(client),
        "summary": {
            "total_available_capital": _number(summary.total_available_capital),
            "liquid_cash": _number(summary.liquid_cash),
            "savings_account": _number(summary.savings_account),
            "investments_value": _number(summary.investments_value),
            "total_monthly_deficits_or_debts": _number(summary.total_monthly_deficits_or_debts),
            "net_worth_trend_30d": summary.net_worth_trend_30d,
        } if summary else None,
        "upcoming_payments": [
            {"payment_id": item.payment_id, "label": item.label, "amount": _number(item.amount), "due_date": _date(item.due_date), "status": item.status}
            for item in payments
        ],
        "investments": [
            {"investment_id": item.investment_id, "holding_name": item.holding_name, "holding_type": item.holding_type, "asset_value": _number(item.asset_value), "return_ytd": item.return_ytd}
            for item in investments
        ],
        "transactions": [
            {"transaction_id": item.transaction_id, "tx_date": _date(item.tx_date), "merchant": item.merchant, "category": item.category, "amount": _number(item.amount), "tx_type": item.tx_type, "flag_ai_trigger": item.flag_ai_trigger}
            for item in transactions
        ],
        "loans": [
            {"loan_id": item.loan_id, "loan_type": item.loan_type, "initial_amount": _number(item.initial_amount), "remaining_balance": _number(item.remaining_balance), "monthly_payment": _number(item.monthly_payment), "status": item.status, "start_date": _date(item.start_date), "end_date": _date(item.end_date)}
            for item in loans
        ],
        "insurances": [
            {"insurance_id": item.insurance_id, "contract_code": item.contract_code, "insurance_type": item.insurance_type, "monthly_premium": _number(item.monthly_premium), "status": item.status, "start_date": _date(item.start_date), "end_date": _date(item.end_date)}
            for item in insurances
        ],
        "nudges": [_serialize_nudge(item) for item in nudges],
        "source": "mariadb",
    }
