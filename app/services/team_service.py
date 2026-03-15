from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.team import create_team, get_team_by_id, list_teams_for_user, soft_delete_team
from app.crud.team_member import (
    create_team_member,
    delete_team_member,
    get_team_member,
    list_team_members,
)
from app.crud.user import get_user_by_id
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.user import User
from app.schemas.team import TeamCreate


def create_team_with_creator_as_admin(
    db: Session,
    *,
    team_in: TeamCreate,
    current_user: User,
) -> Team:
    team = create_team(db, team_in=team_in, created_by=current_user.id)

    create_team_member(
        db,
        team_id=team.id,
        user_id=current_user.id,
        role=TeamRole.ADMIN,
    )

    return team


def get_team_for_member_or_404(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> Team:
    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found.",
        )

    membership = get_team_member(db, team_id=team_id, user_id=current_user.id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team.",
        )

    return team


def require_team_admin(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> TeamMember:
    membership = get_team_member(db, team_id=team_id, user_id=current_user.id)

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team.",
        )

    if membership.role != TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return membership


def list_current_user_teams(db: Session, *, current_user: User) -> list[Team]:
    return list_teams_for_user(db, user_id=current_user.id)


def add_member_to_team(
    db: Session,
    *,
    team_id: int,
    user_id: int,
    role: TeamRole,
    current_user: User,
) -> TeamMember:
    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found.",
        )

    require_team_admin(db, team_id=team_id, current_user=current_user)

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    existing_membership = get_team_member(db, team_id=team_id, user_id=user_id)
    if existing_membership is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team.",
        )

    return create_team_member(db, team_id=team_id, user_id=user_id, role=role)


def remove_member_from_team(
    db: Session,
    *,
    team_id: int,
    user_id: int,
    current_user: User,
) -> None:
    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found.",
        )

    require_team_admin(db, team_id=team_id, current_user=current_user)

    membership = get_team_member(db, team_id=team_id, user_id=user_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found.",
        )

    # Prevent admin from removing themselves if they are the only admin.
    if membership.user_id == current_user.id and membership.role == TeamRole.ADMIN:
        members = list_team_members(db, team_id=team_id)
        admin_count = sum(1 for member in members if member.role == TeamRole.ADMIN)
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the only admin from the team.",
            )

    delete_team_member(db, membership=membership)


def list_members_for_team(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> list[TeamMember]:
    get_team_for_member_or_404(db, team_id=team_id, current_user=current_user)
    return list_team_members(db, team_id=team_id)


def delete_team_for_admin(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> None:
    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found.",
        )

    require_team_admin(db, team_id=team_id, current_user=current_user)
    soft_delete_team(db, team=team)