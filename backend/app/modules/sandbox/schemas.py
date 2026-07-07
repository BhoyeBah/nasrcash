from pydantic import BaseModel


class SimulateFailureRequest(BaseModel):
    reason: str = "insufficient_funds"
