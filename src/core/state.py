import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import UserState


class StateService:
    def get_state(self, db: Session, user_id: int) -> tuple[str, dict]:
        state = db.get(UserState, user_id)
        if not state:
            state = UserState(user_id=user_id, state="MAIN_MENU", payload="{}")
            db.add(state)
            db.flush()
        try:
            payload = json.loads(state.payload or "{}")
        except json.JSONDecodeError:
            payload = {}
        return state.state, payload

    def set_state(self, db: Session, user_id: int, state_name: str, payload: dict | None = None) -> None:
        state = db.get(UserState, user_id)
        if not state:
            state = UserState(user_id=user_id)
            db.add(state)
        state.state = state_name
        state.payload = json.dumps(payload or {}, ensure_ascii=False)

    def clear(self, db: Session, user_id: int) -> None:
        self.set_state(db, user_id, "MAIN_MENU", {})
