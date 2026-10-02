from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class GroupBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    contribution_amount: float = Field(..., gt=0)
    frequency: str = Field(default="weekly", pattern="^(weekly|monthly)$")
    start_date: date


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: int
    organizer_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupDetailRead(GroupRead):
    organizer: UserRead
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)
