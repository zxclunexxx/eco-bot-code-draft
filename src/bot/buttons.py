from enum import StrEnum
from typing import Any


class Callback(StrEnum):
    MAIN_MENU = "main_menu"
    RECYCLING_POINTS = "recycling_points"
    ECO_TIP = "eco_tip"
    QUIZ = "quiz"
    PROFILE = "profile"
    HELP = "help"

    AUTH_REGISTER = "auth_register"
    AUTH_LOGIN = "auth_login"
    AUTH_ACCEPT_PERSONAL_DATA = "auth_accept_personal_data"

    ECO_TIP_SUBSCRIBE = "eco_tip_subscribe"
    ECO_TIP_UNSUBSCRIBE = "eco_tip_unsubscribe"
    ECO_TIP_CONFIRM_SUBSCRIBE = "eco_tip_confirm_subscribe"

    QUIZ_NEXT = "quiz_next"
    QUIZ_EXIT = "quiz_exit"

    ADMIN_PANEL = "admin_panel"
    RATING = "rating"


def button(text: str, callback: str | Callback) -> dict[str, str]:
    return {"text": text, "callback": str(callback)}


def url_button(text: str, url: str) -> dict[str, str]:
    return {"text": text, "url": url}


def keyboard(rows: list[list[dict[str, Any]]]) -> dict[str, Any]:
    return {"type": "inline_keyboard", "rows": rows}


def main_menu(is_admin: bool = False) -> dict[str, Any]:
    rows = [
        [button("♻️ Пункты приёма", Callback.RECYCLING_POINTS)],
        [button("🌱 Эко-совет дня", Callback.ECO_TIP)],
        [button("🧠 Викторина", Callback.QUIZ)],
        [button("🏆 Рейтинг", Callback.RATING)],
        [button("👤 Профиль", Callback.PROFILE), button("ℹ️ Помощь", Callback.HELP)],
    ]
    if is_admin:
        rows.append([button("⚙️ Админ-панель", Callback.ADMIN_PANEL)])
    return keyboard(rows)


def auth_menu() -> dict[str, Any]:
    return keyboard([
        [button("📝 Регистрация", Callback.AUTH_REGISTER)],
        [button("🔐 Вход", Callback.AUTH_LOGIN)],
        [button("⬅️ Главное меню", Callback.MAIN_MENU)],
    ])


def personal_data_menu() -> dict[str, Any]:
    return keyboard([
        [button("✅ Согласен", Callback.AUTH_ACCEPT_PERSONAL_DATA)],
        [button("⬅️ Главное меню", Callback.MAIN_MENU)],
    ])


def materials_menu(materials: list[str]) -> dict[str, Any]:
    rows = [[button(name, f"material:{name}")] for name in materials]
    rows.append([button("⬅️ Главное меню", Callback.MAIN_MENU)])
    return keyboard(rows)


def request_location_menu() -> dict[str, Any]:
    return keyboard([
        [button("📍 Отправить геолокацию", "send_location")],
        [button("🔎 Показать без геолокации", "no_location")],
        [button("⬅️ Главное меню", Callback.MAIN_MENU)],
    ])


def recycling_points_menu(items: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for item in items:
        title = item["name"]
        if item.get("distance_m") is not None:
            distance = item["distance_m"]
            title = f"{title} — {distance} м" if distance < 1000 else f"{title} — {distance / 1000:.1f} км"
        rows.append([button(title, f"point:{item['id']}")])
    rows.append([button("⬅️ Главное меню", Callback.MAIN_MENU)])
    return keyboard(rows)


def point_details_menu(route_url: str) -> dict[str, Any]:
    return keyboard([
        [url_button("🗺️ Построить маршрут", route_url)],
        [button("⬅️ Главное меню", Callback.MAIN_MENU)],
    ])


def eco_tip_menu(is_subscribed: bool) -> dict[str, Any]:
    rows = []
    if is_subscribed:
        rows.append([button("🔕 Отключить рассылку", Callback.ECO_TIP_UNSUBSCRIBE)])
    else:
        rows.append([button("✅ Подписаться", Callback.ECO_TIP_SUBSCRIBE)])
    rows.append([button("⬅️ Главное меню", Callback.MAIN_MENU)])
    return keyboard(rows)


def confirm_subscribe_menu() -> dict[str, Any]:
    return keyboard([
        [button("✅ Подтвердить подписку", Callback.ECO_TIP_CONFIRM_SUBSCRIBE)],
        [button("⬅️ Главное меню", Callback.MAIN_MENU)],
    ])


def quiz_answer_menu(options: list[str]) -> dict[str, Any]:
    rows = [[button(option, f"quiz_answer:{i}")] for i, option in enumerate(options)]
    rows.append([button("⬅️ Главное меню", Callback.QUIZ_EXIT)])
    return keyboard(rows)


def quiz_after_answer_menu() -> dict[str, Any]:
    return keyboard([
        [button("➡️ Следующий вопрос", Callback.QUIZ_NEXT)],
        [button("⬅️ Главное меню", Callback.QUIZ_EXIT)],
    ])
