from typing import Any, Literal

from pydantic import BaseModel


class BotUpdate(BaseModel):
    user_id: int
    chat_id: int
    type: Literal["message", "callback", "location"] = "message"
    text: str | None = None
    callback: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    full_name: str | None = None


class BotResponse(BaseModel):
    chat_id: int
    text: str
    keyboard: dict[str, Any] | None = None
