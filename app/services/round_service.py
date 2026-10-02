from datetime import datetime, timezone
from typing import List
from app.core.exceptions import BusinessRuleException, ForbiddenException, NotFoundException
from app.models.round import Round
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.contribution_repository import ContributionRepository
from app.schemas.round import RoundDetailRead


class RoundService:
    def __init__(
        self,
        round_repo: RoundRepository,
        group_repo: GroupRepository,
        membership_repo: MembershipRepository,
        contribution_repo: ContributionRepository,
    ):
        self.round_repo = round_repo
        self.group_repo = group_repo
        self.membership_repo = membership_repo
        self.contribution_repo = contribution_repo

    async def get_rounds_for_group(self, group_id: int) -> List[Round]:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found")
        return await self.round_repo.get_by_group_id(group_id)

    async def get_round_detail(self, round_id: int) -> RoundDetailRead:
        round_obj = await self.round_repo.get_by_id(round_id)
        if not round_obj:
            raise NotFoundException(f"Round {round_id} not found")
        return RoundDetailRead.model_validate(round_obj)

    async def close_round(self, current_user: User, round_id: int) -> RoundDetailRead:
        round_obj = await self.round_repo.get_by_id(round_id)
        if not round_obj:
            raise NotFoundException(f"Round {round_id} not found")

        group = await self.group_repo.get_by_id(round_obj.group_id)
        if not group:
            raise NotFoundException(f"Group {round_obj.group_id} not found")

        if group.organizer_id != current_user.id:
            raise ForbiddenException("Only the group organizer can close rounds")

        if round_obj.status == "closed":
            raise BusinessRuleException("Round is already closed")

        memberships = await self.membership_repo.get_group_memberships(group.id)
        contributions = await self.contribution_repo.get_by_round_id(round_id)

        # Ensure all group members have logged contributions for this round
        contributed_member_ids = {c.member_id for c in contributions if c.status == "paid"}
        all_member_ids = {m.user_id for m in memberships}

        missing_member_ids = all_member_ids - contributed_member_ids
        if missing_member_ids:
            raise BusinessRuleException(
                f"Cannot close round: {len(missing_member_ids)} member(s) have not contributed yet."
            )

        # Close the round
        round_obj.status = "closed"
        round_obj.closed_at = datetime.now(timezone.utc)
        await self.round_repo.update(round_obj)

        # Mark payout member membership as paid out
        payout_membership = await self.membership_repo.get_by_group_and_user(
            group.id, round_obj.payout_member_id
        )
        if payout_membership:
            payout_membership.has_been_paid_out = True
            await self.membership_repo.update_all([payout_membership])

        # Check if all rounds for this group are closed -> group complete
        all_rounds = await self.round_repo.get_by_group_id(group.id)
        if all(r.status == "closed" for r in all_rounds):
            group.status = "completed"
            await self.group_repo.update(group)

        updated_round = await self.round_repo.get_by_id(round_id)
        return RoundDetailRead.model_validate(updated_round)
