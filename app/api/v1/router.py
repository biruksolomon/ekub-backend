from fastapi import APIRouter

from app.api.v1 import auth, groups, rounds, members

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(rounds.router, tags=["Rounds & Contributions"])
api_router.include_router(members.router, tags=["Members"])
