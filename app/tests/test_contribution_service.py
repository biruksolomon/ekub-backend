from datetime import date
import pytest
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.user_repository import UserRepository
from app.repositories.contribution_repository import ContributionRepository
from app.schemas.group import GroupCreate
from app.schemas.contribution import LogContributionRequest
from app.services.group_service import GroupService
from app.services.contribution_service import ContributionService


@pytest.mark.asyncio
async def test_log_contribution_and_member_status(db_session):
    user_repo = UserRepository(db_session)
    group_repo = GroupRepository(db_session)
    membership_repo = MembershipRepository(db_session)
    round_repo = RoundRepository(db_session)
    contrib_repo = ContributionRepository(db_session)

    u1 = await user_repo.create(
        User(name="Org User", email="ou@ekub.com", phone="0933000001", hashed_password="pw", role="organizer")
    )
    u2 = await user_repo.create(
        User(name="Mem User", email="mu@ekub.com", phone="0933000002", hashed_password="pw", role="member")
    )

    group_svc = GroupService(group_repo, membership_repo, round_repo, user_repo)
    contrib_svc = ContributionService(contrib_repo, round_repo, group_repo, membership_repo)

    grp = await group_svc.create_group(
        u1, GroupCreate(name="Status Test Group", contribution_amount=2000.0, frequency="monthly", start_date=date.today())
    )
    await group_svc.add_member(u1, grp.id, u2.id)
    rounds = await group_svc.start_group(u1, grp.id)
    r1 = rounds[0]

    # Log contribution for u2
    c = await contrib_svc.log_contribution(
        u1, r1.id, LogContributionRequest(member_id=u2.id, amount=2000.0, status="paid")
    )
    assert c.member_id == u2.id
    assert c.amount == 2000.0
    assert c.status == "paid"

    # Get status for u2
    st = await contrib_svc.get_member_status(u2.id, grp.id)
    assert st.user_id == u2.id
    assert st.total_contributions_paid == 2000.0
    assert st.rounds_paid_count == 1
    assert st.total_rounds_count == 2
