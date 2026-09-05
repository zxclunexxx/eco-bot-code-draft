# Eco Bot — кодовые наработки

Каркас backend-проекта для экологического бота: главное меню, регистрация/вход, пункты приёма, эко-советы, викторина, баллы, админка и интеграции.

## Что уже есть

- `main.py` — запуск FastAPI-приложения и webhook.
- `bot/buttons.py` — все кнопки и callback-коды.
- `bot/router.py` — маршрутизация входящих событий.
- `core/database.py` — подключение к БД, модели, начальные данные.
- `modules/auth` — регистрация, вход, проверка пользователя.
- `modules/recycling` — поиск пунктов приёма, сортировка по расстоянию.
- `modules/newsletter` — подписка/отписка на эко-советы.
- `modules/quiz` — запуск викторины, проверка ответа, начисление баллов.
- `modules/points` — рейтинг пользователей.
- `modules/admin` — базовая проверка админа и статистика.
- `integrations/ai.py` — заглушка под ИИ, которую можно заменить на реальный API.
- `integrations/internet_search.py` — заглушка под интернет-поиск.
- `integrations/maps.py` — генерация ссылок на маршрут.

## Быстрый запуск

```bash
cd eco_bot_code_draft
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

Открыть проверку:

```bash
curl http://127.0.0.1:8000/health
```

Пример webhook-запроса:

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "message", "text": "/start"}'
```

## Важное

Сейчас это MVP-каркас. Реальную отправку сообщений в MAX Bot API нужно подключить в `src/bot/gateway.py`.
