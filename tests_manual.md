# Ручные тесты через curl

## 1. Старт

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "message", "text": "/start", "full_name": "Артём"}'
```

## 2. Пункты приёма

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "callback", "callback": "recycling_points"}'
```

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "callback", "callback": "material:Пластик"}'
```

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "location", "latitude": 55.751244, "longitude": 37.618423}'
```

## 3. Регистрация

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "callback", "callback": "auth_register"}'
```

Далее отправить логин и пароль обычными сообщениями.

## 4. Викторина

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "chat_id": 1, "type": "callback", "callback": "quiz"}'
```
