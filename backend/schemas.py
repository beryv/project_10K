from typing import Literal
from pydantic import BaseModel


class ChatRequest(BaseModel):
  client_id: str
  message: str


class NudgeStatusUpdate(BaseModel):
  status: Literal["PENDING", "ACCEPTED", "DISMISSED"]
