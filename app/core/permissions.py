from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.team import get_team_by_id
from app.crud.team_member import get_team_member
from app.models.task import Task
from app.models.team_member import TeamMember, TeamRole
from app.models.user import User
from app.crud.comment import get_comment_by_id
from app.crud.task import get_task_by_id
from app.models.comment import Comment


def get_team_membership_or_none(
    db: Session,
    *,
    team_id: int,
    user_id: int,
) -> TeamMember | None:
    return get_team_member(db, team_id=team_id, user_id=user_id)


def require_team_membership(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> TeamMember:
    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found.",
        )

    membership = get_team_membership_or_none(
        db,
        team_id=team_id,
        user_id=current_user.id,
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team.",
        )

    return membership


def require_team_admin(
    db: Session,
    *,
    team_id: int,
    current_user: User,
) -> TeamMember:
    membership = require_team_membership(
        db,
        team_id=team_id,
        current_user=current_user,
    )

    if membership.role != TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return membership


def require_task_view_permission(
    db: Session,
    *,
    task: Task,
    current_user: User,
) -> None:
    if task.team_id is None:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this task.",
            )
        return

    require_team_membership(db, team_id=task.team_id, current_user=current_user)


def require_task_edit_permission(
    db: Session,
    *,
    task: Task,
    current_user: User,
) -> None:
    if task.team_id is None:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this task.",
            )
        return

    membership = require_team_membership(
        db,
        team_id=task.team_id,
        current_user=current_user,
    )

    if task.created_by == current_user.id:
        return

    if membership.role == TeamRole.ADMIN:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to modify this task.",
    )

def ensure_assignee_in_same_team(
    db: Session,
    *,
    team_id: int,
    assignee_user_id: int,
) -> None:
    membership = get_team_membership_or_none(
        db,
        team_id=team_id,
        user_id=assignee_user_id,
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignee must belong to the same team.",
        )
    
def require_comment_create_permission(
    db: Session,
    *,
    task: Task,
    current_user: User,
) -> None:
    require_task_view_permission(db, task=task, current_user=current_user)


def require_comment_edit_permission(
    db: Session,
    *,
    comment: Comment,
    current_user: User,
    task: Task,
) -> None:
    if comment.user_id == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to edit this comment.",
    )


def require_comment_delete_permission(
    db: Session,
    *,
    comment: Comment,
    current_user: User,
    task: Task,
) -> None:
    if comment.user_id == current_user.id:
        return

    if task.team_id is not None:
        membership = get_team_membership_or_none(
            db,
            team_id=task.team_id,
            user_id=current_user.id,
        )
        if membership and membership.role == TeamRole.ADMIN:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to delete this comment.",
    )    