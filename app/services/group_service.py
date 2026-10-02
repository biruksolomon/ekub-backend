import random
from datetime import timedelta
from typing import List
from app.core.exceptions import BusinessRuleException, ForbiddenException, NotFoundException
from app.models.group import Group
from app.models.membership import Membership
from app.models.round import Round
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.round_repository import RoundRepository
from app.repositories.user_repository import UserRepository
from app.schemas.group import GroupCreate, GroupRead, GroupDetailRead
from app.schemas.membership import MembershipRead


class GroupService:
    def __init__(
        self,
        group_repo: GroupRepository,
        membership_repo: MembershipRepository,
        round_repo: RoundRepository,
        user_repo: UserRepository,
    ):
        self.group_repo = group_repo
        self.membership_repo = membership_repo
        self.round_repo = round_repo
        self.user_repo = user_repo

    async def create_group(self, current_user: User, req: GroupCreate) -> GroupRead:
        group = Group(
            name=req.name,
            organizer_id=current_user.id,
            contribution_amount=req.contribution_amount,
            frequency=req.frequency,
            start_date=req.start_date,
            status="pending",
        )
        created_group = await self.group_repo.create(group)

        # Organizer automatically becomes member #1
        organizer_membership = Membership(
            group_id=created_group.id,
            user_id=current_user.id,
            turn_order=1,
            has_been_paid_out=False,
        )
        await self.membership_repo.create(organizer_membership)

        return GroupRead.model_validate(created_group)

    async def get_group_detail(self, group_id: int) -> GroupDetailRead:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found")

        memberships = await self.membership_repo.get_group_memberships(group_id)
        group_detail = GroupDetailRead.model_validate(group)
        group_detail.member_count = len(memberships)
        return group_detail

    async def add_member(self, current_user: User, group_id: int, user_id_to_add: int) -> MembershipRead:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found")

        if group.organizer_id != current_user.id:
            raise ForbiddenException("Only the organizer can add members to this group")

        if group.status != "pending":
            raise BusinessRuleException("Cannot add members to a group that has already started or completed")

        user_to_add = await self.user_repo.get_by_id(user_id_to_add)
        if not user_to_add:
            raise NotFoundException(f"User {user_id_to_add} not found")

        existing = await self.membership_repo.get_by_group_and_user(group_id, user_id_to_add)
        if existing:
            raise BusinessRuleException("User is already a member of this group")

        existing_memberships = await self.membership_repo.get_group_memberships(group_id)
        next_turn = len(existing_memberships) + 1

        new_membership = Membership(
            group_id=group_id,
            user_id=user_id_to_add,
            turn_order=next_turn,
            has_been_paid_out=False,
        )
        created_membership = await self.membership_repo.create(new_membership)
        return MembershipRead.model_validate(created_membership)

    async def start_group(self, current_user: User, group_id: int, randomize_turn_order: bool = False) -> List[Round]:
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found")

        if group.organizer_id != current_user.id:
            raise ForbiddenException("Only the organizer can start this group")

        if group.status != "pending":
            raise BusinessRuleException("Group has already been started or completed")

        memberships = await self.membership_repo.get_group_memberships(group_id)
        if len(memberships) < 2:
            raise BusinessRuleException("An Ekub group must have at least 2 members before starting")

        # Set turn order
        if randomize_turn_order:
            member_indices = list(range(len(memberships)))
            random.shuffle(member_indices)
            for new_turn, idx in enumerate(member_indices, start=1):
                memberships[idx].turn_order = new_turn
        else:
            for idx, mem in enumerate(memberships, start=1):
                mem.turn_order = idx

        await self.membership_repo.update_all(memberships)

        # Sort memberships by turn_order
        memberships.sort(key=lambda m: m.turn_order)

        # Generate rounds
        rounds_to_create: List[Round] = []
        current_due_date = group.start_date

        for round_num, mem in enumerate(memberships, start=1):
            rounds_to_create.append(
                Round(
                    group_id=group.id,
                    round_number=round_num,
                    due_date=current_due_date,
                    payout_member_id=mem.user_id,
                    status="open",
                )
            )

            # Calculate next due date
            if group.frequency == "monthly":
                # Approx 30 days or next month
                current_due_date = current_due_date + timedelta(days=30)
            else:
                # weekly
                current_due_date = current_due_date + timedelta(days=7)

        created_rounds = await self.round_repo.create_many(rounds_to_create)

        # Mark group active
        group.status = "active"
        await self.group_repo.update(group)

        return created_rounds
