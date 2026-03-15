from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate


def create_team(db: Session, *, team_in: TeamCreate, created_by: int) -> Team:
    team = Team(
        name=team_in.name,
        description=team_in.description,
        created_by=created_by,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team_by_id(db: Session, team_id: int) -> Team | None:
    statement = select(Team).where(
        Team.id == team_id,
        Team.deleted_at.is_(None),
    )
    return db.execute(statement).scalar_one_or_none()


def update_team(db: Session, *, team: Team, team_in: TeamUpdate) -> Team:
    update_data = team_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(team, field, value)

    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def soft_delete_team(db: Session, *, team: Team) -> Team:
    team.deleted_at = datetime.utcnow()
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def list_teams_for_user(db: Session, *, user_id: int) -> list[Team]:
    from app.models.team_member import TeamMember

    statement = (
        select(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .where(
            TeamMember.user_id == user_id,
            Team.deleted_at.is_(None),
        )
        .order_by(Team.created_at.desc())
    )
    return list(db.execute(statement).scalars().all())