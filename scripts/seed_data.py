from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.comment import Comment


def seed_data():
    db: Session = SessionLocal()

    try:
        # Avoid duplicate seeding
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("Seed data already exists.")
            return

        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("strongpass123"),
            is_active=True,
        )
        member = User(
            username="member",
            email="member@example.com",
            hashed_password=hash_password("strongpass123"),
            is_active=True,
        )
        outsider = User(
            username="outsider",
            email="outsider@example.com",
            hashed_password=hash_password("strongpass123"),
            is_active=True,
        )

        db.add_all([admin, member, outsider])
        db.commit()
        db.refresh(admin)
        db.refresh(member)
        db.refresh(outsider)

        team = Team(
            name="Backend Team",
            description="Handles API development",
            created_by=admin.id,
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        admin_membership = TeamMember(
            team_id=team.id,
            user_id=admin.id,
            role=TeamRole.ADMIN,
        )
        member_membership = TeamMember(
            team_id=team.id,
            user_id=member.id,
            role=TeamRole.MEMBER,
        )
        db.add_all([admin_membership, member_membership])
        db.commit()

        personal_task = Task(
            title="Prepare release notes",
            description="Write release notes for next deployment",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            created_by=admin.id,
        )

        team_task = Task(
            title="Implement team comments",
            description="Add comment endpoints and moderation rules",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            created_by=admin.id,
            team_id=team.id,
            assigned_to=member.id,
        )

        db.add_all([personal_task, team_task])
        db.commit()
        db.refresh(personal_task)
        db.refresh(team_task)

        comment = Comment(
            task_id=team_task.id,
            user_id=member.id,
            content="I have started working on this task.",
        )
        db.add(comment)
        db.commit()

        print("Seed data created successfully.")
        print("Users:")
        print("  admin@example.com / strongpass123")
        print("  member@example.com / strongpass123")
        print("  outsider@example.com / strongpass123")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()