import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import EcoTip, EcoTipSubscription, User


class NewsletterService:
    def is_subscribed(self, db: Session, user_id: int) -> bool:
        subscription = db.get(EcoTipSubscription, user_id)
        return bool(subscription and subscription.is_active)

    def subscribe(self, db: Session, user_id: int, hour: int = 9, minute: int = 0) -> None:
        subscription = db.get(EcoTipSubscription, user_id)
        if not subscription:
            subscription = EcoTipSubscription(user_id=user_id)
            db.add(subscription)

        subscription.is_active = True
        subscription.send_hour = hour
        subscription.send_minute = minute

    def unsubscribe(self, db: Session, user_id: int) -> None:
        subscription = db.get(EcoTipSubscription, user_id)
        if subscription:
            subscription.is_active = False

    def get_tip_of_day(self, db: Session) -> str:
        tips = db.scalars(select(EcoTip).where(EcoTip.is_active.is_(True))).all()
        if not tips:
            return "Сегодня совет простой: начните с малого — отсортируйте один вид отходов."
        return random.choice(tips).text

    def get_active_subscribers(self, db: Session) -> list[User]:
        return db.scalars(
            select(User)
            .join(EcoTipSubscription, EcoTipSubscription.user_id == User.id)
            .where(EcoTipSubscription.is_active.is_(True))
        ).all()
