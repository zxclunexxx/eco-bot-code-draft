from sqlalchemy.orm import Session

from src.bot import buttons
from src.bot.buttons import Callback
from src.bot.gateway import BotGateway
from src.bot.schemas import BotResponse, BotUpdate
from src.config import get_settings
from src.core.state import StateService
from src.modules.admin.service import AdminService
from src.modules.auth.service import AuthService
from src.modules.newsletter.service import NewsletterService
from src.modules.points.service import PointsService
from src.modules.quiz.service import QuizService
from src.modules.recycling.service import RecyclingPointService


class BotRouter:
    def __init__(self):
        self.gateway = BotGateway()
        self.auth = AuthService()
        self.states = StateService()
        self.recycling = RecyclingPointService()
        self.newsletter = NewsletterService()
        self.quiz = QuizService()
        self.points = PointsService()
        self.admin = AdminService()

    def handle(self, db: Session, update: BotUpdate) -> BotResponse:
        user = self.auth.get_or_create_user(
            db=db,
            messenger_user_id=update.user_id,
            chat_id=update.chat_id,
            full_name=update.full_name,
        )

        if update.type == "message" and update.text == "/start":
            self.states.clear(db, user.id)
            return self.gateway.message(
                update.chat_id,
                "Привет! Я экологический бот. Выберите раздел:",
                buttons.main_menu(is_admin=self.admin.is_admin(update.user_id)),
            )

        if update.type == "callback":
            return self._handle_callback(db, update, user)

        if update.type == "location":
            return self._handle_location(db, update, user)

        return self._handle_text(db, update, user)

    def _handle_callback(self, db: Session, update: BotUpdate, user) -> BotResponse:
        callback = update.callback or ""

        if callback == Callback.MAIN_MENU:
            self.states.clear(db, user.id)
            return self.gateway.message(
                update.chat_id,
                "Главное меню:",
                buttons.main_menu(is_admin=self.admin.is_admin(update.user_id)),
            )

        if callback == Callback.RECYCLING_POINTS:
            materials = self.recycling.list_materials(db)
            self.states.set_state(db, user.id, "WAITING_MATERIAL_CHOICE", {})
            return self.gateway.message(
                update.chat_id,
                "Выберите сырьё, которое хотите сдать:",
                buttons.materials_menu(materials),
            )

        if callback.startswith("material:"):
            material = callback.split(":", 1)[1]
            self.states.set_state(db, user.id, "WAITING_LOCATION", {"material": material})
            return self.gateway.message(
                update.chat_id,
                f"Вы выбрали: {material}. Отправьте геолокацию или посмотрите пункты без неё.",
                buttons.request_location_menu(),
            )

        if callback == "no_location":
            _, payload = self.states.get_state(db, user.id)
            material = payload.get("material")
            items = self.recycling.find_by_material(db, material)
            self.states.set_state(db, user.id, "WAITING_RECYCLING_POINT_CHOICE", {"material": material})
            return self.gateway.message(
                update.chat_id,
                "Пункты приёма отсортированы по алфавиту:",
                buttons.recycling_points_menu(items),
            )

        if callback.startswith("point:"):
            point_id = int(callback.split(":", 1)[1])
            _, payload = self.states.get_state(db, user.id)
            point = self.recycling.get_point_details(
                db,
                point_id,
                user_lat=payload.get("lat"),
                user_lon=payload.get("lon"),
            )
            if not point:
                return self.gateway.message(update.chat_id, "Пункт приёма не найден.")

            text = (
                f"♻️ {point['name']}\n"
                f"Адрес: {point['address']}\n"
                f"График: {point['working_hours']}\n"
                f"Условия: {point['conditions']}"
            )
            return self.gateway.message(update.chat_id, text, buttons.point_details_menu(point["route_url"]))

        if callback == Callback.ECO_TIP:
            is_subscribed = self.newsletter.is_subscribed(db, user.id)
            tip = self.newsletter.get_tip_of_day(db)
            return self.gateway.message(
                update.chat_id,
                f"Эко-совет 🌱\n\n{tip}\n\nМожно подписаться на ежедневную рассылку в 9:00.",
                buttons.eco_tip_menu(is_subscribed),
            )

        if callback == Callback.ECO_TIP_SUBSCRIBE:
            return self.gateway.message(
                update.chat_id,
                "Советы будут приходить каждый день в 9:00. Подтвердить подписку?",
                buttons.confirm_subscribe_menu(),
            )

        if callback == Callback.ECO_TIP_CONFIRM_SUBSCRIBE:
            settings = get_settings()
            self.newsletter.subscribe(db, user.id, settings.newsletter_hour, settings.newsletter_minute)
            return self.gateway.message(
                update.chat_id,
                "Подписка подключена. Эко-советы будут приходить каждый день в 9:00.",
                buttons.main_menu(is_admin=self.admin.is_admin(update.user_id)),
            )

        if callback == Callback.ECO_TIP_UNSUBSCRIBE:
            self.newsletter.unsubscribe(db, user.id)
            return self.gateway.message(update.chat_id, "Рассылка отключена.", buttons.main_menu())

        if callback == Callback.QUIZ:
            if not self.auth.is_registered(user):
                self.states.set_state(db, user.id, "AUTH_REQUIRED", {"next": "quiz"})
                return self.gateway.message(
                    update.chat_id,
                    "Для викторины нужно зарегистрироваться или войти.",
                    buttons.auth_menu(),
                )

            session, options = self.quiz.start_question(db, user)
            self.states.set_state(db, user.id, "WAITING_QUIZ_ANSWER", {"session_id": session.id, "options": options})
            return self.gateway.message(
                update.chat_id,
                f"Вопрос:\n{session.question}",
                buttons.quiz_answer_menu(options),
            )

        if callback.startswith("quiz_answer:"):
            _, payload = self.states.get_state(db, user.id)
            options = payload.get("options", [])
            index = int(callback.split(":", 1)[1])
            if index >= len(options):
                return self.gateway.message(update.chat_id, "Такого варианта ответа нет.")
            result = self.quiz.check_text_answer(db, user, options[index])
            self.states.set_state(db, user.id, "QUIZ_ANSWERED", {})
            return self.gateway.message(update.chat_id, result["message"], buttons.quiz_after_answer_menu())

        if callback == Callback.QUIZ_NEXT:
            session, options = self.quiz.start_question(db, user)
            self.states.set_state(db, user.id, "WAITING_QUIZ_ANSWER", {"session_id": session.id, "options": options})
            return self.gateway.message(update.chat_id, f"Следующий вопрос:\n{session.question}", buttons.quiz_answer_menu(options))

        if callback == Callback.QUIZ_EXIT:
            self.quiz.finish(db, user)
            self.states.clear(db, user.id)
            return self.gateway.message(update.chat_id, "Викторина завершена.", buttons.main_menu())

        if callback == Callback.AUTH_REGISTER:
            self.states.set_state(db, user.id, "WAITING_REGISTER_LOGIN", {})
            return self.gateway.message(update.chat_id, "Введите логин для регистрации:")

        if callback == Callback.AUTH_LOGIN:
            self.states.set_state(db, user.id, "WAITING_LOGIN_LOGIN", {})
            return self.gateway.message(update.chat_id, "Введите логин:")

        if callback == Callback.RATING:
            rating = self.points.get_rating(db)
            if not rating:
                text = "Рейтинг пока пуст."
            else:
                lines = [f"{row['place']}. {row['name']} — {row['points']} баллов" for row in rating]
                text = "🏆 Рейтинг\n\n" + "\n".join(lines)
            return self.gateway.message(update.chat_id, text, buttons.main_menu())

        if callback == Callback.PROFILE:
            text = (
                f"👤 Профиль\n"
                f"Имя: {user.full_name or 'не указано'}\n"
                f"Логин: {user.login or 'не зарегистрирован'}\n"
                f"Очки: {user.points}\n"
                f"Правильные ответы: {user.correct_answers}\n"
                f"Неправильные ответы: {user.wrong_answers}"
            )
            return self.gateway.message(update.chat_id, text, buttons.main_menu())

        if callback == Callback.ADMIN_PANEL:
            if not self.admin.is_admin(update.user_id):
                return self.gateway.message(update.chat_id, "Доступ запрещён.")
            stats = self.admin.get_statistics(db)
            text = (
                "⚙️ Админ-панель\n"
                f"Пользователей: {stats['users_count']}\n"
                f"Зарегистрировано: {stats['registered_count']}\n"
                f"Пунктов приёма: {stats['recycling_points_count']}\n"
                f"Подписок на советы: {stats['subscriptions_count']}"
            )
            return self.gateway.message(update.chat_id, text, buttons.main_menu(is_admin=True))

        if callback == Callback.HELP:
            return self.gateway.message(
                update.chat_id,
                "Помощь: выберите раздел в меню. Для викторины нужна регистрация.",
                buttons.main_menu(is_admin=self.admin.is_admin(update.user_id)),
            )

        return self.gateway.message(update.chat_id, "Неизвестная команда.", buttons.main_menu())

    def _handle_text(self, db: Session, update: BotUpdate, user) -> BotResponse:
        state, payload = self.states.get_state(db, user.id)
        text = update.text or ""

        if state == "WAITING_REGISTER_LOGIN":
            self.states.set_state(db, user.id, "WAITING_REGISTER_PASSWORD", {"login": text})
            return self.gateway.message(update.chat_id, "Введите пароль:")

        if state == "WAITING_REGISTER_PASSWORD":
            login = payload.get("login", "")
            ok, message = self.auth.register(db, user, login, text)
            if not ok:
                self.states.set_state(db, user.id, "WAITING_REGISTER_LOGIN", {})
                return self.gateway.message(update.chat_id, message + "\nВведите другой логин:")

            next_screen = payload.get("next") or "main_menu"
            self.states.clear(db, user.id)
            return self.gateway.message(update.chat_id, message, buttons.main_menu())

        if state == "WAITING_LOGIN_LOGIN":
            self.states.set_state(db, user.id, "WAITING_LOGIN_PASSWORD", {"login": text})
            return self.gateway.message(update.chat_id, "Введите пароль:")

        if state == "WAITING_LOGIN_PASSWORD":
            login = payload.get("login", "")
            ok, logged_user, message = self.auth.login(db, login, text)
            if not ok:
                self.states.set_state(db, user.id, "WAITING_LOGIN_LOGIN", {})
                return self.gateway.message(update.chat_id, message + "\nПопробуйте снова. Введите логин:")

            self.states.clear(db, user.id)
            return self.gateway.message(update.chat_id, message, buttons.main_menu())

        if state == "WAITING_QUIZ_ANSWER":
            result = self.quiz.check_text_answer(db, user, text)
            self.states.set_state(db, user.id, "QUIZ_ANSWERED", {})
            return self.gateway.message(update.chat_id, result["message"], buttons.quiz_after_answer_menu())

        return self.gateway.message(
            update.chat_id,
            "Я не понял сообщение. Выберите действие в меню.",
            buttons.main_menu(is_admin=self.admin.is_admin(update.user_id)),
        )

    def _handle_location(self, db: Session, update: BotUpdate, user) -> BotResponse:
        _, payload = self.states.get_state(db, user.id)
        material = payload.get("material")
        if not material:
            return self.gateway.message(update.chat_id, "Сначала выберите тип сырья.")

        if update.latitude is None or update.longitude is None:
            return self.gateway.message(update.chat_id, "Не удалось получить координаты.")

        items = self.recycling.find_by_material(db, material, update.latitude, update.longitude)
        self.states.set_state(
            db,
            user.id,
            "WAITING_RECYCLING_POINT_CHOICE",
            {"material": material, "lat": update.latitude, "lon": update.longitude},
        )
        return self.gateway.message(
            update.chat_id,
            "Ближайшие пункты приёма:",
            buttons.recycling_points_menu(items),
        )
