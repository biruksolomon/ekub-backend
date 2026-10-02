from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_group_service
from app.models.user import User
from app.schemas.group import GroupCreate, GroupRead, GroupDetailRead
from app.schemas.membership import AddMemberRequest, MembershipRead
from app.schemas.round import RoundRead
from app.services.group_service import GroupService

router = APIRouter()


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    req: GroupCreate,
    current_user: User = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    return await group_service.create_group(current_user, req)


@router.get("/{id}", response_model=GroupDetailRead)
async def get_group_detail(
    id: int,
    current_user: User = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    return await group_service.get_group_detail(id)


@router.post("/{id}/members", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    id: int,
    req: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    return await group_service.add_member(current_user, id, req.user_id)


@router.post("/{id}/start", response_model=List[RoundRead])
async def start_group(
    id: int,
    randomize: bool = Query(default=False, description="Randomize member turn order"),
    current_user: User = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    rounds = await group_service.start_group(current_user, id, randomize_turn_order=randomize)
    return [RoundRead.model_validate(r) for r in rounds]
