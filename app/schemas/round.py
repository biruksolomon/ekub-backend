from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead
from app.schemas.contribution import ContributionRead


class RoundRead(BaseModel):
    id: int
    group_id: int
    round_number: int
    due_date: date
    payout_member_id: int
    status: str
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoundDetailRead(RoundRead):
    payout_member: UserRead
    contributions: List[ContributionRead] = []

    model_config = ConfigDict(from_attributes=True)
