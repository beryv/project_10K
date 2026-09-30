from typing import Literal
from pydantic import BaseModel


class NudgeStatusUpdate(BaseModel):
  status: Literal["ACCEPTED", "DISMISSED"]
