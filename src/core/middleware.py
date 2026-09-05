from time import time


class RateLimitMiddleware:
    def __init__(self, limit_per_minute: int = 20):
        self.limit_per_minute = limit_per_minute
        self._history: dict[int, list[float]] = {}

    def is_allowed(self, user_id: int) -> bool:
        now = time()
        window_start = now - 60
        history = [item for item in self._history.get(user_id, []) if item >= window_start]
        if len(history) >= self.limit_per_minute:
            self._history[user_id] = history
            return False

        history.append(now)
        self._history[user_id] = history
        return True
