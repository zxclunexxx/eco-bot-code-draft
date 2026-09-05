from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.core.models import EcoTipSubscription, RecyclingPoint, User


class AdminService:
    def is_admin(self, messenger_user_id: int) -> bool:
        return messenger_user_id in get_settings().admin_id_list

    def get_statistics(self, db: Session) -> dict:
        users_count = db.scalar(select(func.count(User.id))) or 0
        registered_count = db.scalar(select(func.count(User.id)).where(User.is_registered.is_(True))) or 0
        points_count = db.scalar(select(func.count(RecyclingPoint.id)).where(RecyclingPoint.is_active.is_(True))) or 0
        subscriptions_count = db.scalar(
            select(func.count(EcoTipSubscription.user_id)).where(EcoTipSubscription.is_active.is_(True))
        ) or 0

        return {
            "users_count": users_count,
            "registered_count": registered_count,
            "recycling_points_count": points_count,
            "subscriptions_count": subscriptions_count,
        }
