from datetime import datetime, date, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.membership import Membership
    from app.models.round import Round


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    contribution_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="weekly")  # weekly or monthly
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, active, completed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organizer: Mapped["User"] = relationship("User", back_populates="organized_groups")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="group", cascade="all, delete-orphan")
    rounds: Mapped[List["Round"]] = relationship("Round", back_populates="group", cascade="all, delete-orphan")
