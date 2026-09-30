import os
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from classifier import generate_chatbot_response, predict_nudges
from database import get_db
from repository import ClientRepository
from schemas import ChatRequest, NudgeStatusUpdate


app = FastAPI(
    title="KBC Pulse AI API",
    description="API de démonstration KBC Pulse avec MariaDB, fallback JSON et classifier.py.",
    version="1.1.0",
)


def get_repository(db: Session) -> ClientRepository:
  return ClientRepository(db)


def get_client_context(repository: ClientRepository, client_id: str) -> dict:
  context = repository.get_client_context(client_id)
  if context is None:
    raise HTTPException(status_code=404, detail="Client not found")
  return context


def build_dashboard(repository: ClientRepository, client_id: str) -> dict:
  context = get_client_context(repository, client_id)
  context["nudges"] = predict_nudges(context)
  return context


@app.get("/", tags=["System"])
def read_root():
  return {"service": "KBC Pulse AI API", "docs": "/docs"}


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
  try:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "mariadb"}
  except SQLAlchemyError:
    db.rollback()
    return {"status": "degraded", "database": "json-fallback"}


@app.get("/clients", tags=["KBC Pulse"])
@app.get("/v1/clients", tags=["KBC Pulse"])
@app.get("/pulse/clients", include_in_schema=False)
def list_clients(db: Session = Depends(get_db)):
  return get_repository(db).list_clients()


@app.get("/clients/{client_id}/dashboard", tags=["KBC Pulse"])
@app.get("/v1/clients/{client_id}/dashboard", tags=["KBC Pulse"])
@app.get("/pulse/clients/{client_id}/dashboard", include_in_schema=False)
def get_client_dashboard(client_id: str, db: Session = Depends(get_db)):
  return build_dashboard(get_repository(db), client_id)


@app.get("/clients/{client_id}/nudges", tags=["KBC Pulse"])
@app.get("/v1/clients/{client_id}/nudges", tags=["KBC Pulse"])
@app.get("/pulse/clients/{client_id}/nudges", include_in_schema=False)
def list_client_nudges(client_id: str, db: Session = Depends(get_db)):
  context = get_client_context(get_repository(db), client_id)
  return predict_nudges(context)


@app.patch("/clients/{client_id}/nudges/{nudge_id}", tags=["KBC Pulse"])
@app.patch("/v1/clients/{client_id}/nudges/{nudge_id}", tags=["KBC Pulse"])
@app.patch("/pulse/clients/{client_id}/nudges/{nudge_id}", include_in_schema=False)
def update_nudge_status(
    client_id: str,
    nudge_id: str,
    payload: NudgeStatusUpdate,
    db: Session = Depends(get_db),
):
  repository = get_repository(db)
  updated = repository.update_nudge_status(client_id, nudge_id, payload.status)
  if updated is None:
    raise HTTPException(status_code=404, detail="Suggestion not found")
  return updated


@app.post("/chat", tags=["KBC Pulse Copilot"])
@app.post("/v1/chat", tags=["KBC Pulse Copilot"])
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
  context = get_client_context(get_repository(db), payload.client_id)
  response = generate_chatbot_response(context, payload.message)
  return {
      "client_id": payload.client_id,
      "response": response,
      "source": context.get("source", "mariadb"),
      "llm_enabled": bool(os.getenv("GEMINI_API_KEY")),
  }
