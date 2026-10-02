from datetime import date
import pytest
from app.core.exceptions import BusinessRuleException
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.user_repository import UserRepository
from app.repositories.contribution_repository import ContributionRepository
from app.schemas.group import GroupCreate
from app.schemas.contribution import LogContributionRequest
from app.services.group_service import GroupService
from app.services.round_service import RoundService
from app.services.contribution_service import ContributionService


@pytest.mark.asyncio
async def test_close_round_eligibility(db_session):
    user_repo = UserRepository(db_session)
    group_repo = GroupRepository(db_session)
    membership_repo = MembershipRepository(db_session)
    round_repo = RoundRepository(db_session)
    contrib_repo = ContributionRepository(db_session)

    u1 = await user_repo.create(
        User(name="Org", email="o@ekub.com", phone="0922000001", hashed_password="pw", role="organizer")
    )
    u2 = await user_repo.create(
        User(name="Mem", email="m@ekub.com", phone="0922000002", hashed_password="pw", role="member")
    )

    group_svc = GroupService(group_repo, membership_repo, round_repo, user_repo)
    round_svc = RoundService(round_repo, group_repo, membership_repo, contrib_repo)
    contrib_svc = ContributionService(contrib_repo, round_repo, group_repo, membership_repo)

    grp = await group_svc.create_group(
        u1, GroupCreate(name="Round Test Group", contribution_amount=500.0, frequency="weekly", start_date=date.today())
    )
    await group_svc.add_member(u1, grp.id, u2.id)
    rounds = await group_svc.start_group(u1, grp.id)
    r1 = rounds[0]

    # Trying to close round without all contributions should raise BusinessRuleException
    with pytest.raises(BusinessRuleException) as exc_info:
        await round_svc.close_round(u1, r1.id)
    assert "member(s) have not contributed yet" in str(exc_info.value)

    # Log both member contributions
    await contrib_svc.log_contribution(u1, r1.id, LogContributionRequest(member_id=u1.id, amount=500.0, status="paid"))
    await contrib_svc.log_contribution(u1, r1.id, LogContributionRequest(member_id=u2.id, amount=500.0, status="paid"))

    # Now closing round succeeds
    closed_r1 = await round_svc.close_round(u1, r1.id)
    assert closed_r1.status == "closed"
