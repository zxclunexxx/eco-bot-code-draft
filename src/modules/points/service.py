from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import User


class PointsService:
    def add_points(self, user: User, amount: int) -> None:
        user.points += amount

    def get_rating(self, db: Session, limit: int = 10) -> list[dict]:
        users = db.scalars(
            select(User)
            .where(User.is_registered.is_(True))
            .order_by(User.points.desc())
            .limit(limit)
        ).all()

        return [
            {
                "place": index + 1,
                "name": user.full_name or user.login or f"Пользователь {user.id}",
                "points": user.points,
            }
            for index, user in enumerate(users)
        ]
