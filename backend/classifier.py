import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai


SYSTEM_PROMPT = """You are KBC Pulse Copilot, a careful financial information assistant.
Use only the supplied client data. Never invent balances, products, transactions, eligibility, rates, or approvals. Explain that financing and product suitability require a bank review. Do not give regulated investment or credit advice. Respond in the user's language, concisely and helpfully."""

_client: genai.Client | None = None


def init() -> genai.Client | None:
  """Initialize Gemini only when a key is configured; the demo works without it."""
  global _client
  load_dotenv()
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    _client = None
    return None
  _client = genai.Client(api_key=api_key)
  return _client


def _get_client() -> genai.Client | None:
  load_dotenv()
  if _client is None and os.getenv("GEMINI_API_KEY"):
    return init()
  return _client


def _nudge_templates() -> dict[str, dict[str, Any]]:
  return {
      "NEW_CAR_PURCHASE": {
          "nudge_id": "nudge_01", "priority": "HIGH", "category": "Assurance Auto",
          "title": "Achat véhicule détecté — Assurance Auto KBC Proactive",
          "description": "Un achat de véhicule a été détecté. Vérifiez que votre nouveau véhicule est couvert avant de prendre la route.",
          "explainability_reason": "Transaction automobile récente détectée; aucun contrat d'assurance auto actif n'est associé au profil.",
          "confidence_score": 0.96,
      },
      "REAL_ESTATE_INTENT": {
          "nudge_id": "nudge_02", "priority": "HIGH", "category": "Prêt Hypothécaire",
          "title": "Préparation à votre futur projet immobilier",
          "description": "Vos revenus et votre capital peuvent justifier une simulation de financement immobilier, sous réserve d'une analyse complète.",
          "explainability_reason": "Dépense notariale détectée et revenus réguliers enregistrés dans le profil.",
          "confidence_score": 0.89,
      },
      "GREEN_HOME_INVESTMENT": {
          "nudge_id": "nudge_03", "priority": "HIGH", "category": "Prêt Vert",
          "title": "Financement Rénovation Énergétique — Prêt Vert KBC",
          "description": "Un paiement lié à une installation énergétique a été détecté. Explorez les options de financement disponibles.",
          "explainability_reason": "Acompte EcoSolar détecté dans l'historique des transactions.",
          "confidence_score": 0.93,
      },
      "TUITION_FEE": {
          "nudge_id": "nudge_04", "priority": "MEDIUM", "category": "Épargne Études",
          "title": "Plan d'épargne pour les études supérieures",
          "description": "Des frais universitaires ont été détectés. Vous pouvez explorer des solutions pour planifier les prochaines échéances.",
          "explainability_reason": "Paiement à une université détecté dans l'historique récent.",
          "confidence_score": 0.85,
      },
      "EXCESS_LIQUIDITY_RECEIVED": {
          "nudge_id": "nudge_05", "priority": "HIGH", "category": "Gestion de Patrimoine",
          "title": "Placement Épargne & Private Banking",
          "description": "Un important apport de liquidités a été détecté. Un conseiller peut présenter les options adaptées à votre profil.",
          "explainability_reason": "Virement entrant important détecté; profil investisseur et niveau d'endettement disponibles.",
          "confidence_score": 0.95,
      },
  }


def predict_nudges(client_data: dict[str, Any]) -> list[dict[str, Any]]:
  """Classify observed transaction triggers into explainable, ranked suggestions."""
  client = client_data.get("client", {})
  if not client.get("ai_consent_active", True):
    return []

  existing = {item.get("nudge_id"): item for item in client_data.get("nudges", [])}
  templates = _nudge_templates()
  detected: dict[str, dict[str, Any]] = {}
  insurances = client_data.get("insurances", [])
  has_active_auto_cover = any(
      item.get("status") == "ACTIVE" and "auto" in item.get("insurance_type", "").lower()
      for item in insurances
  )

  for transaction in client_data.get("transactions", []):
    trigger = transaction.get("flag_ai_trigger")
    template = templates.get(trigger)
    if not template:
      continue
    if trigger == "NEW_CAR_PURCHASE" and has_active_auto_cover:
      continue

    nudge_id = template["nudge_id"]
    saved = existing.get(nudge_id, {})
    detected[nudge_id] = {
        **template,
        "description": saved.get("description") or template["description"],
        "explainability_reason": saved.get("explainability_reason") or template["explainability_reason"],
        "confidence_score": float(saved.get("confidence_score", template["confidence_score"])),
        "status": saved.get("status", "PENDING"),
        "created_at": saved.get("created_at"),
    }

  priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
  return sorted(
      detected.values(),
      key=lambda item: (priority_order.get(item["priority"], 3), item["nudge_id"]),
  )


def _format_eur(value: Any) -> str:
  try:
    return f"{float(value):,.0f} €".replace(",", " ")
  except (TypeError, ValueError):
    return "montant indisponible"


def _fallback_chat_response(client_data: dict[str, Any], user_message: str) -> str:
  client = client_data.get("client", {})
  summary = client_data.get("summary") or {}
  name = client.get("first_name", "")
  capital = _format_eur(summary.get("total_available_capital"))
  income = _format_eur(client.get("monthly_net_income"))
  active_loans = [loan for loan in client_data.get("loans", []) if loan.get("status") == "ACTIVE"]
  insurance_names = [
      item.get("insurance_type", "")
      for item in client_data.get("insurances", [])
      if item.get("status") == "ACTIVE"
  ]
  question = user_message.casefold()

  if any(word in question for word in ("appartement", "immobilier", "emprunt", "financer", "prêt")):
    loan_text = (
        ", ".join(loan["loan_type"] for loan in active_loans)
        if active_loans else "aucun prêt actif enregistré"
    )
    return (
        f"{name}, votre profil indique {capital} de capital disponible et {income} de revenus nets mensuels. "
        f"Il comporte {loan_text}. Ces éléments permettent d'amorcer une simulation, mais ne suffisent pas "
        "à confirmer une capacité d'emprunt ou une approbation. Un conseiller KBC devra étudier vos charges, "
        "votre apport et le projet complet."
    )
  if any(word in question for word in ("assurance", "couverture", "contrat")):
    contracts = ", ".join(insurance_names) if insurance_names else "aucun contrat actif enregistré"
    return f"Pour le profil {name}, les contrats actifs enregistrés sont : {contracts}. Vérifiez les garanties et exclusions dans les conditions de chaque contrat."
  if any(word in question for word in ("invest", "épargne", "placement", "bourse")):
    holdings = client_data.get("investments", [])
    invested = sum(float(item.get("asset_value", 0)) for item in holdings)
    names = ", ".join(item.get("holding_name", "") for item in holdings)
    return (
        f"Le profil {name} affiche {_format_eur(invested)} d'investissements répartis entre {names or 'aucun placement listé'}. "
        "Les performances passées ne préjugent pas des performances futures; cette synthèse n'est pas un conseil d'investissement."
    )
  return (
      f"Je peux vous aider à lire votre profil. Il indique {capital} de capital disponible, "
      f"{income} de revenus nets mensuels et {len(insurance_names)} contrat(s) d'assurance actif(s). "
      "Posez-moi une question sur vos échéances, prêts, assurances ou placements."
  )


def generate_chatbot_response(client_data: dict[str, Any], user_message: str) -> str:
  """Answer with Gemini when configured, otherwise return a contextual local response."""
  message = user_message.strip()
  if not message:
    return "Écrivez une question sur vos comptes, prêts, assurances ou placements."

  client = _get_client()
  if client is None:
    return _fallback_chat_response(client_data, message)

  prompt = (
      "Réponds à cette question avec le contexte JSON complet ci-dessous. "
      "N'utilise que les informations présentes, distingue les faits des hypothèses, "
      "et rappelle qu'une décision de crédit exige une analyse par un conseiller.\n\n"
      f"CONTEXTE_CLIENT={json.dumps(client_data, ensure_ascii=False, default=str)}\n\n"
      f"QUESTION={message}"
  )
  try:
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
        config=genai.types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=prompt,
    )
    answer = (response.text or "").strip()
    return answer or _fallback_chat_response(client_data, message)
  except Exception:
    return _fallback_chat_response(client_data, message)
