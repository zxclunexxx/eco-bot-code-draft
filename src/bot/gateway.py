from src.bot.schemas import BotResponse


class BotGateway:
    """Адаптер отправки сообщений.

    Сейчас возвращает BotResponse для тестирования через HTTP.
    Для реального MAX Bot API здесь нужно сделать HTTP-запрос к API мессенджера.
    """

    def message(self, chat_id: int, text: str, keyboard: dict | None = None) -> BotResponse:
        return BotResponse(chat_id=chat_id, text=text, keyboard=keyboard)
