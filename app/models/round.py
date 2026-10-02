from datetime import date, datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User
    from app.models.contribution import Contribution


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    payout_member_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, closed
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    group: Mapped["Group"] = relationship("Group", back_populates="rounds")
    payout_member: Mapped["User"] = relationship("User")
    contributions: Mapped[List["Contribution"]] = relationship("Contribution", back_populates="round", cascade="all, delete-orphan")
