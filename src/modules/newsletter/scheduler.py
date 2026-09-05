from apscheduler.schedulers.background import BackgroundScheduler

from src.bot.gateway import BotGateway
from src.config import get_settings
from src.core.database import db_session
from src.modules.newsletter.service import NewsletterService


def send_daily_tips() -> None:
    service = NewsletterService()
    gateway = BotGateway()

    with db_session() as db:
        tip = service.get_tip_of_day(db)
        users = service.get_active_subscribers(db)
        for user in users:
            gateway.message(user.chat_id, f"Эко-совет дня 🌱\n\n{tip}")


def create_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        send_daily_tips,
        trigger="cron",
        hour=settings.newsletter_hour,
        minute=settings.newsletter_minute,
        id="daily_eco_tips",
        replace_existing=True,
    )
    return scheduler
