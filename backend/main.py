from datetime import datetime
from database import get_db
from fastapi import Depends, FastAPI, HTTPException
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
from schemas import NudgeStatusUpdate
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(
    title="KBC Pulse AI API",
    description="Démonstration bancaire basée sur les données MariaDB KBC Pulse.",
    version="1.0.0",
)


@app.get("/", tags=["System"])
def read_root():
  return {"service": "KBC Pulse AI API", "docs": "/docs"}


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
  db.execute(text("SELECT 1"))
  return {"status": "ok", "database": "mariadb"}


def get_client_or_404(db: Session, client_id: str) -> Client:
  client = db.query(Client).filter(Client.client_id == client_id).first()
  if not client:
    raise HTTPException(status_code=404, detail="Client not found")
  return client


def serialize_client(client: Client):
  return {
      "client_id": client.client_id,
      "first_name": client.first_name,
      "last_name": client.last_name,
      "display_name": f"{client.first_name} {client.last_name}",
      "age": client.age,
      "persona_type": client.persona_type,
      "civil_status": client.civil_status,
      "profession": client.profession,
      "monthly_net_income": float(client.monthly_net_income),
      "investor_profile": client.investor_profile,
      "kbc_segment": client.kbc_segment,
      "ai_consent_active": bool(client.ai_consent_active),
  }


def serialize_nudge(nudge: AIPredictionNudge):
  return {
      "nudge_id": nudge.nudge_id,
      "priority": nudge.priority,
      "category": nudge.category,
      "title": nudge.title,
      "description": nudge.description,
      "explainability_reason": nudge.explainability_reason,
      "confidence_score": float(nudge.confidence_score),
      "status": nudge.status,
      "created_at": nudge.created_at.isoformat() if nudge.created_at else None,
  }


@app.get("/pulse/clients", tags=["KBC Pulse"])
def list_clients(db: Session = Depends(get_db)):
  """List seeded demo profiles for the profile selector."""
  clients = db.query(Client).order_by(Client.age.asc()).all()
  return [serialize_client(client) for client in clients]


@app.get("/pulse/clients/{client_id}/dashboard", tags=["KBC Pulse"])
def get_client_dashboard(client_id: str, db: Session = Depends(get_db)):
  client = get_client_or_404(db, client_id)
  summary = (
      db.query(FinancialSummary)
      .filter(FinancialSummary.client_id == client_id)
      .order_by(FinancialSummary.summary_id.desc())
      .first()
  )
  payments = (
      db.query(UpcomingPayment)
      .filter(
          UpcomingPayment.client_id == client_id,
          UpcomingPayment.status.in_(["PLANNED", "PROCESSING"]),
      )
      .order_by(UpcomingPayment.due_date.asc(), UpcomingPayment.payment_id.asc())
      .all()
  )
  investments = (
      db.query(Investment)
      .filter(Investment.client_id == client_id)
      .order_by(Investment.investment_id.asc())
      .all()
  )
  transactions = (
      db.query(Transaction)
      .filter(Transaction.client_id == client_id)
      .order_by(Transaction.tx_date.desc(), Transaction.transaction_id.desc())
      .all()
  )
  loans = (
      db.query(Loan)
      .filter(Loan.client_id == client_id)
      .order_by(Loan.loan_id.asc())
      .all()
  )
  insurances = (
      db.query(Insurance)
      .filter(Insurance.client_id == client_id)
      .order_by(Insurance.insurance_id.asc())
      .all()
  )
  nudges = (
      db.query(AIPredictionNudge)
      .filter(AIPredictionNudge.client_id == client_id)
      .order_by(AIPredictionNudge.priority.asc(), AIPredictionNudge.created_at.asc())
      .all()
  )

  return {
      "client": serialize_client(client),
      "summary": {
          "total_available_capital": float(summary.total_available_capital),
          "liquid_cash": float(summary.liquid_cash),
          "savings_account": float(summary.savings_account),
          "investments_value": float(summary.investments_value),
          "total_monthly_deficits_or_debts": float(summary.total_monthly_deficits_or_debts),
          "net_worth_trend_30d": summary.net_worth_trend_30d,
      } if summary else None,
      "upcoming_payments": [
          {
              "payment_id": payment.payment_id,
              "label": payment.label,
              "amount": float(payment.amount),
              "due_date": payment.due_date.isoformat(),
              "status": payment.status,
          }
          for payment in payments
      ],
      "investments": [
          {
              "investment_id": item.investment_id,
              "holding_name": item.holding_name,
              "holding_type": item.holding_type,
              "asset_value": float(item.asset_value),
              "return_ytd": item.return_ytd,
          }
          for item in investments
      ],
      "transactions": [
          {
              "transaction_id": item.transaction_id,
              "tx_date": item.tx_date.isoformat(),
              "merchant": item.merchant,
              "category": item.category,
              "amount": float(item.amount),
              "tx_type": item.tx_type,
              "flag_ai_trigger": item.flag_ai_trigger,
          }
          for item in transactions
      ],
      "loans": [
          {
              "loan_id": item.loan_id,
              "loan_type": item.loan_type,
              "initial_amount": float(item.initial_amount),
              "remaining_balance": float(item.remaining_balance),
              "monthly_payment": float(item.monthly_payment),
              "status": item.status,
              "start_date": item.start_date.isoformat(),
              "end_date": item.end_date.isoformat(),
          }
          for item in loans
      ],
      "insurances": [
          {
              "insurance_id": item.insurance_id,
              "contract_code": item.contract_code,
              "insurance_type": item.insurance_type,
              "monthly_premium": float(item.monthly_premium),
              "status": item.status,
              "start_date": item.start_date.isoformat(),
              "end_date": item.end_date.isoformat() if item.end_date else None,
          }
          for item in insurances
      ],
      "nudges": [serialize_nudge(nudge) for nudge in nudges],
  }


@app.get("/pulse/clients/{client_id}/nudges", tags=["KBC Pulse"])
def list_client_nudges(client_id: str, db: Session = Depends(get_db)):
  get_client_or_404(db, client_id)
  nudges = (
      db.query(AIPredictionNudge)
      .filter(AIPredictionNudge.client_id == client_id)
      .order_by(AIPredictionNudge.priority.asc(), AIPredictionNudge.created_at.asc())
      .all()
  )
  return [serialize_nudge(nudge) for nudge in nudges]


@app.patch("/pulse/clients/{client_id}/nudges/{nudge_id}", tags=["KBC Pulse"])
def update_nudge_status(
    client_id: str,
    nudge_id: str,
    payload: NudgeStatusUpdate,
    db: Session = Depends(get_db),
):
  get_client_or_404(db, client_id)
  nudge = (
      db.query(AIPredictionNudge)
      .filter(
          AIPredictionNudge.client_id == client_id,
          AIPredictionNudge.nudge_id == nudge_id,
      )
      .first()
  )
  if not nudge:
    raise HTTPException(status_code=404, detail="Suggestion not found")
  nudge.status = payload.status
  db.commit()
  db.refresh(nudge)
  return serialize_nudge(nudge)
