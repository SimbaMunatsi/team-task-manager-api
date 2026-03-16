from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import (
    require_comment_create_permission,
    require_comment_delete_permission,
    require_comment_edit_permission,
    require_task_view_permission,
)
from app.crud.comment import (
    create_comment,
    get_comment_by_id,
    list_comments_for_task,
    soft_delete_comment,
    update_comment,
)
from app.crud.task import get_task_by_id
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate


def get_task_or_404(db: Session, *, task_id: int) -> Task:
    task = get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return task


def create_comment_for_task(
    db: Session,
    *,
    task_id: int,
    comment_in: CommentCreate,
    current_user: User,
) -> Comment:
    task = get_task_or_404(db, task_id=task_id)
    require_comment_create_permission(db, task=task, current_user=current_user)

    return create_comment(
        db,
        task_id=task.id,
        user_id=current_user.id,
        comment_in=comment_in,
    )


def list_comments_for_visible_task(
    db: Session,
    *,
    task_id: int,
    current_user: User,
) -> list[Comment]:
    task = get_task_or_404(db, task_id=task_id)
    require_task_view_permission(db, task=task, current_user=current_user)
    return list_comments_for_task(db, task_id=task.id)


def update_comment_for_user(
    db: Session,
    *,
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: User,
) -> Comment:
    comment = get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    task = get_task_or_404(db, task_id=comment.task_id)
    require_task_view_permission(db, task=task, current_user=current_user)
    require_comment_edit_permission(
        db,
        comment=comment,
        current_user=current_user,
        task=task,
    )

    return update_comment(db, comment=comment, comment_in=comment_in)


def delete_comment_for_user(
    db: Session,
    *,
    comment_id: int,
    current_user: User,
) -> None:
    comment = get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    task = get_task_or_404(db, task_id=comment.task_id)
    require_task_view_permission(db, task=task, current_user=current_user)
    require_comment_delete_permission(
        db,
        comment=comment,
        current_user=current_user,
        task=task,
    )

    soft_delete_comment(db, comment=comment)