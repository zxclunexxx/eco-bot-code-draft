import re
from datetime import datetime
from uuid import uuid4


def make_uuid() -> str:
    return str(uuid4())


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def trim_text(text: str, max_length: int = 4000) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def is_valid_url(url: str) -> bool:
    return bool(re.match(r"^https?://", url))


def escape_markdown(text: str) -> str:
    for ch in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        text = text.replace(ch, "\\" + ch)
    return text
