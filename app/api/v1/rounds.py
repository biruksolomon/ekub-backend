from typing import List
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_round_service, get_contribution_service
from app.models.user import User
from app.schemas.contribution import LogContributionRequest, ContributionRead
from app.schemas.round import RoundRead, RoundDetailRead
from app.services.round_service import RoundService
from app.services.contribution_service import ContributionService

router = APIRouter()


@router.get("/groups/{group_id}/rounds", response_model=List[RoundRead])
async def get_group_rounds(
    group_id: int,
    current_user: User = Depends(get_current_user),
    round_service: RoundService = Depends(get_round_service),
):
    rounds = await round_service.get_rounds_for_group(group_id)
    return [RoundRead.model_validate(r) for r in rounds]


@router.get("/rounds/{id}", response_model=RoundDetailRead)
async def get_round_detail(
    id: int,
    current_user: User = Depends(get_current_user),
    round_service: RoundService = Depends(get_round_service),
):
    return await round_service.get_round_detail(id)


@router.post("/rounds/{id}/contributions", response_model=ContributionRead, status_code=status.HTTP_201_CREATED)
async def log_contribution(
    id: int,
    req: LogContributionRequest,
    current_user: User = Depends(get_current_user),
    contribution_service: ContributionService = Depends(get_contribution_service),
):
    return await contribution_service.log_contribution(current_user, id, req)


@router.post("/rounds/{id}/close", response_model=RoundDetailRead)
async def close_round(
    id: int,
    current_user: User = Depends(get_current_user),
    round_service: RoundService = Depends(get_round_service),
):
    return await round_service.close_round(current_user, id)
