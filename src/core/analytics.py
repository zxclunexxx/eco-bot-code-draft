import json
from sqlalchemy.orm import Session

from src.core.models import AnalyticsEvent


class AnalyticsService:
    def track(self, db: Session, event_type: str, user_id: int | None = None, payload: dict | None = None) -> None:
        db.add(AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            payload=json.dumps(payload or {}, ensure_ascii=False),
        ))
