from datetime import datetime, timezone
from typing import List
from app.core.exceptions import BusinessRuleException, ForbiddenException, NotFoundException
from app.models.contribution import Contribution
from app.models.user import User
from app.repositories.contribution_repository import ContributionRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.schemas.contribution import ContributionRead, LogContributionRequest
from app.schemas.membership import MemberStatusRead


class ContributionService:
    def __init__(
        self,
        contribution_repo: ContributionRepository,
        round_repo: RoundRepository,
        group_repo: GroupRepository,
        membership_repo: MembershipRepository,
    ):
        self.contribution_repo = contribution_repo
        self.round_repo = round_repo
        self.group_repo = group_repo
        self.membership_repo = membership_repo

    async def log_contribution(
        self, current_user: User, round_id: int, req: LogContributionRequest
    ) -> ContributionRead:
        round_obj = await self.round_repo.get_by_id(round_id)
        if not round_obj:
            raise NotFoundException(f"Round {round_id} not found")

        group = await self.group_repo.get_by_id(round_obj.group_id)
        if not group:
            raise NotFoundException(f"Group {round_obj.group_id} not found")

        if group.organizer_id != current_user.id:
            raise ForbiddenException("Only the group organizer can log contributions")

        if round_obj.status == "closed":
            raise BusinessRuleException("Cannot log contribution for a closed round")

        membership = await self.membership_repo.get_by_group_and_user(group.id, req.member_id)
        if not membership:
            raise BusinessRuleException("User is not a member of this group")

        existing_contrib = await self.contribution_repo.get_by_round_and_member(
            round_id, req.member_id
        )

        if existing_contrib:
            existing_contrib.amount = req.amount
            existing_contrib.status = req.status
            existing_contrib.paid_at = datetime.now(timezone.utc)
            updated = await self.contribution_repo.update(existing_contrib)
            return ContributionRead.model_validate(updated)
        else:
            contrib = Contribution(
                round_id=round_id,
                member_id=req.member_id,
                amount=req.amount,
                status=req.status,
            )
            created = await self.contribution_repo.create(contrib)
            return ContributionRead.model_validate(created)

    async def get_member_status(self, user_id: int, group_id: int) -> MemberStatusRead:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found")

        membership = await self.membership_repo.get_by_group_and_user(group_id, user_id)
        if not membership:
            raise NotFoundException("User is not a member of this group")

        rounds = await self.round_repo.get_by_group_id(group_id)
        contributions = await self.contribution_repo.get_by_member_and_group(user_id, group_id)

        paid_contributions = [c for c in contributions if c.status == "paid"]
        total_paid = sum(c.amount for c in paid_contributions)

        next_payout_date = None
        for r in rounds:
            if r.payout_member_id == user_id:
                next_payout_date = str(r.due_date)
                break

        return MemberStatusRead(
            group_id=group_id,
            group_name=group.name,
            user_id=user_id,
            turn_order=membership.turn_order,
            has_been_paid_out=membership.has_been_paid_out,
            total_contributions_paid=total_paid,
            rounds_paid_count=len(paid_contributions),
            total_rounds_count=len(rounds),
            next_payout_date=next_payout_date,
        )
