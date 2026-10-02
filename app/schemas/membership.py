from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead


class AddMemberRequest(BaseModel):
    user_id: int


class MembershipRead(BaseModel):
    id: int
    group_id: int
    user_id: int
    turn_order: Optional[int] = None
    has_been_paid_out: bool
    joined_at: datetime
    user: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)


class MemberStatusRead(BaseModel):
    group_id: int
    group_name: str
    user_id: int
    turn_order: Optional[int]
    has_been_paid_out: bool
    total_contributions_paid: float
    rounds_paid_count: int
    total_rounds_count: int
    next_payout_date: Optional[str] = None
