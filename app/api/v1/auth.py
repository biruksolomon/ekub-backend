from typing import Union
from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register(req)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        return await auth_service.login(email=username, password=password)
    else:
        json_data = await request.json()
        req = LoginRequest.model_validate(json_data)
        return await auth_service.login(email=req.email, password=req.password)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserRead.model_validate(current_user)
