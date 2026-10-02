from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.database import AsyncSessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.contribution_repository import ContributionRepository
from app.services.auth_service import AuthService
from app.services.group_service import GroupService
from app.services.round_service import RoundService
from app.services.contribution_service import ContributionService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Could not validate credentials")
    except JWTError:
        raise UnauthorizedException("Could not validate credentials")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))
    if not user:
        raise UnauthorizedException("User not found")
    return user


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    return GroupService(
        GroupRepository(db),
        MembershipRepository(db),
        RoundRepository(db),
        UserRepository(db),
    )


def get_round_service(db: AsyncSession = Depends(get_db)) -> RoundService:
    return RoundService(
        RoundRepository(db),
        GroupRepository(db),
        MembershipRepository(db),
        ContributionRepository(db),
    )


def get_contribution_service(db: AsyncSession = Depends(get_db)) -> ContributionService:
    return ContributionService(
        ContributionRepository(db),
        RoundRepository(db),
        GroupRepository(db),
        MembershipRepository(db),
    )
