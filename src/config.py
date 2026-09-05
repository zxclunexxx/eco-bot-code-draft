from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    database_url: str = "sqlite:///./eco_bot.db"
    admin_ids: str = ""
    newsletter_hour: int = 9
    newsletter_minute: int = 0
    openai_api_key: str = ""
    search_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_id_list(self) -> List[int]:
        if not self.admin_ids:
            return []
        return [
            int(item.strip())
            for item in self.admin_ids.split(",")
            if item.strip().isdigit()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
