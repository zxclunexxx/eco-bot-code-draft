from fastapi import FastAPI

from src.bot.router import BotRouter
from src.bot.schemas import BotResponse, BotUpdate
from src.core.database import db_session, init_db
from src.core.middleware import RateLimitMiddleware
from src.modules.newsletter.scheduler import create_scheduler


app = FastAPI(title="Eco Bot API")
router = BotRouter()
rate_limiter = RateLimitMiddleware(limit_per_minute=30)
scheduler = create_scheduler()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    if not scheduler.running:
        scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook", response_model=BotResponse)
def webhook(update: BotUpdate) -> BotResponse:
    if not rate_limiter.is_allowed(update.user_id):
        return BotResponse(
            chat_id=update.chat_id,
            text="Слишком много запросов. Попробуйте немного позже.",
            keyboard=None,
        )

    with db_session() as db:
        return router.handle(db, update)
