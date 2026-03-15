from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team_member import TeamMember, TeamRole


def create_team_member(
    db: Session,
    *,
    team_id: int,
    user_id: int,
    role: TeamRole = TeamRole.MEMBER,
) -> TeamMember:
    membership = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=role,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_team_member(
    db: Session,
    *,
    team_id: int,
    user_id: int,
) -> TeamMember | None:
    statement = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
    )
    return db.execute(statement).scalar_one_or_none()


def list_team_members(db: Session, *, team_id: int) -> list[TeamMember]:
    statement = (
        select(TeamMember)
        .where(TeamMember.team_id == team_id)
        .order_by(TeamMember.joined_at.asc())
    )
    return list(db.execute(statement).scalars().all())


def delete_team_member(db: Session, *, membership: TeamMember) -> None:
    db.delete(membership)
    db.commit()