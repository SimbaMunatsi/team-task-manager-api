from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TeamRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member_team_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[TeamRole] = mapped_column(
        SqlEnum(TeamRole),
        default=TeamRole.MEMBER,
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )