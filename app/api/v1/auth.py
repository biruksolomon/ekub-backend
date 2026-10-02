from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register(req)


@router.post("/login", response_model=Token)
async def login(
    req: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(req)
