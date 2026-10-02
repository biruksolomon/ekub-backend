from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import BusinessRuleException, UnauthorizedException, NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.schemas.user import UserRead


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, req: RegisterRequest) -> UserRead:
        existing_email = await self.user_repo.get_by_email(req.email)
        if existing_email:
            raise BusinessRuleException("User with this email already exists")

        existing_phone = await self.user_repo.get_by_phone(req.phone)
        if existing_phone:
            raise BusinessRuleException("User with this phone number already exists")

        hashed_password = get_password_hash(req.password)
        user = User(
            name=req.name,
            email=req.email,
            phone=req.phone,
            hashed_password=hashed_password,
            role=req.role,
        )
        created_user = await self.user_repo.create(user)
        return UserRead.model_validate(created_user)

    async def login(self, req: LoginRequest) -> Token:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        token = create_access_token(subject=user.id)
        return Token(access_token=token)

    async def get_current_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
