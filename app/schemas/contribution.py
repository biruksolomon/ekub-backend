from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class LogContributionRequest(BaseModel):
    member_id: int
    amount: float = Field(..., gt=0)
    status: str = Field(default="paid", pattern="^(paid|missed)$")


class ContributionRead(BaseModel):
    id: int
    round_id: int
    member_id: int
    amount: float
    status: str
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)
