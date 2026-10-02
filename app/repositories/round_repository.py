from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.round import Round
from app.models.contribution import Contribution


class RoundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, round_id: int) -> Optional[Round]:
        result = await self.db.execute(
            select(Round)
            .options(
                selectinload(Round.payout_member),
                selectinload(Round.contributions).selectinload(Contribution.member),
                selectinload(Round.group)
            )
            .where(Round.id == round_id)
        )
        return result.scalar_one_or_none()

    async def get_by_group_id(self, group_id: int) -> List[Round]:
        result = await self.db.execute(
            select(Round)
            .options(
                selectinload(Round.payout_member),
                selectinload(Round.contributions)
            )
            .where(Round.group_id == group_id)
            .order_by(Round.round_number.asc())
        )
        return list(result.scalars().all())

    async def create_many(self, rounds: List[Round]) -> List[Round]:
        self.db.add_all(rounds)
        await self.db.flush()
        return rounds

    async def update(self, round_obj: Round) -> Round:
        await self.db.flush()
        await self.db.refresh(round_obj)
        return round_obj
