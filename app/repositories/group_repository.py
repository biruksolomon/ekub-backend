from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.models.membership import Membership


class GroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, group_id: int) -> Optional[Group]:
        result = await self.db.execute(
            select(Group)
            .options(selectinload(Group.organizer), selectinload(Group.memberships).selectinload(Membership.user))
            .where(Group.id == group_id)
        )
        return result.scalar_one_or_none()

    async def create(self, group: Group) -> Group:
        self.db.add(group)
        await self.db.flush()
        await self.db.refresh(group)
        return group

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Group]:
        result = await self.db.execute(
            select(Group)
            .options(selectinload(Group.organizer))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, group: Group) -> Group:
        await self.db.flush()
        await self.db.refresh(group)
        return group
