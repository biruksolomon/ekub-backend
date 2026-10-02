from datetime import date
import pytest
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.user_repository import UserRepository
from app.schemas.group import GroupCreate
from app.services.group_service import GroupService


@pytest.mark.asyncio
async def test_create_and_start_group(db_session):
    user_repo = UserRepository(db_session)
    group_repo = GroupRepository(db_session)
    membership_repo = MembershipRepository(db_session)
    round_repo = RoundRepository(db_session)

    # Create 2 users
    u1 = await user_repo.create(
        User(name="Organizer", email="org@ekub.com", phone="0911000001", hashed_password="pw", role="organizer")
    )
    u2 = await user_repo.create(
        User(name="Member 1", email="mem1@ekub.com", phone="0911000002", hashed_password="pw", role="member")
    )

    service = GroupService(group_repo, membership_repo, round_repo, user_repo)

    # 1. Create group
    group_req = GroupCreate(
        name="Tech Weekly Ekub",
        contribution_amount=1000.0,
        frequency="weekly",
        start_date=date.today(),
    )
    group = await service.create_group(u1, group_req)
    assert group.id is not None
    assert group.status == "pending"

    # 2. Add second member
    mem2 = await service.add_member(u1, group.id, u2.id)
    assert mem2.user_id == u2.id
    assert mem2.turn_order == 2

    # 3. Start group
    rounds = await service.start_group(u1, group.id)
    assert len(rounds) == 2
    assert rounds[0].round_number == 1
    assert rounds[0].payout_member_id == u1.id
    assert rounds[1].round_number == 2
    assert rounds[1].payout_member_id == u2.id
