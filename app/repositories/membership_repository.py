from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership


class MembershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_group_and_user(self, group_id: int, user_id: int) -> Optional[Membership]:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.user), selectinload(Membership.group))
            .where(Membership.group_id == group_id, Membership.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_group_memberships(self, group_id: int) -> List[Membership]:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.group_id == group_id)
            .order_by(Membership.turn_order.asc().nulls_last(), Membership.joined_at.asc())
        )
        return list(result.scalars().all())

    async def get_user_memberships(self, user_id: int) -> List[Membership]:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.group).selectinload(Membership.group.property.mapper.class_.organizer))
            .where(Membership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, membership: Membership) -> Membership:
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def update_all(self, memberships: List[Membership]) -> None:
        await self.db.flush()
