from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contribution import Contribution


class ContributionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_round_and_member(self, round_id: int, member_id: int) -> Optional[Contribution]:
        result = await self.db.execute(
            select(Contribution).where(
                Contribution.round_id == round_id,
                Contribution.member_id == member_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_round_id(self, round_id: int) -> List[Contribution]:
        result = await self.db.execute(
            select(Contribution)
            .options(selectinload(Contribution.member))
            .where(Contribution.round_id == round_id)
        )
        return list(result.scalars().all())

    async def get_by_member_and_group(self, member_id: int, group_id: int) -> List[Contribution]:
        from app.models.round import Round
        result = await self.db.execute(
            select(Contribution)
            .join(Round, Contribution.round_id == Round.id)
            .where(Contribution.member_id == member_id, Round.group_id == group_id)
        )
        return list(result.scalars().all())

    async def create(self, contribution: Contribution) -> Contribution:
        self.db.add(contribution)
        await self.db.flush()
        await self.db.refresh(contribution)
        return contribution

    async def update(self, contribution: Contribution) -> Contribution:
        await self.db.flush()
        await self.db.refresh(contribution)
        return contribution
