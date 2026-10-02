from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_contribution_service
from app.models.user import User
from app.models.membership import Membership
from app.schemas.group import GroupRead
from app.schemas.membership import MemberStatusRead
from app.services.contribution_service import ContributionService

router = APIRouter()


@router.get("/members/me/groups", response_model=List[GroupRead])
async def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.group).selectinload(Membership.group.property.mapper.class_.organizer))
        .where(Membership.user_id == current_user.id)
    )
    memberships = result.scalars().all()
    groups = [m.group for m in memberships if m.group is not None]
    return [GroupRead.model_validate(g) for g in groups]


@router.get("/members/me/groups/{group_id}/status", response_model=MemberStatusRead)
async def get_my_group_status(
    group_id: int,
    current_user: User = Depends(get_current_user),
    contribution_service: ContributionService = Depends(get_contribution_service),
):
    return await contribution_service.get_member_status(current_user.id, group_id)
