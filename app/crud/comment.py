from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


def create_comment(
    db: Session,
    *,
    task_id: int,
    user_id: int,
    comment_in: CommentCreate,
) -> Comment:
    comment = Comment(
        task_id=task_id,
        user_id=user_id,
        content=comment_in.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    statement = select(Comment).where(
        Comment.id == comment_id,
        Comment.deleted_at.is_(None),
    )
    return db.execute(statement).scalar_one_or_none()


def list_comments_for_task(db: Session, *, task_id: int) -> list[Comment]:
    statement = (
        select(Comment)
        .where(
            Comment.task_id == task_id,
            Comment.deleted_at.is_(None),
        )
        .order_by(Comment.created_at.asc())
    )
    return list(db.execute(statement).scalars().all())


def update_comment(
    db: Session,
    *,
    comment: Comment,
    comment_in: CommentUpdate,
) -> Comment:
    comment.content = comment_in.content
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def soft_delete_comment(db: Session, *, comment: Comment) -> Comment:
    comment.deleted_at = datetime.utcnow()
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment