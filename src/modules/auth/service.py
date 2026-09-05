from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def get_or_create_user(
        self,
        db: Session,
        messenger_user_id: int,
        chat_id: int,
        full_name: str | None = None,
    ) -> User:
        user = db.scalar(select(User).where(User.messenger_user_id == messenger_user_id))
        if user:
            return user

        user = User(
            messenger_user_id=messenger_user_id,
            chat_id=chat_id,
            full_name=full_name,
            is_registered=False,
        )
        db.add(user)
        db.flush()
        return user

    def is_registered(self, user: User) -> bool:
        return bool(user.is_registered and user.login and user.password_hash)

    def register(self, db: Session, user: User, login: str, password: str) -> tuple[bool, str]:
        existing = db.scalar(select(User).where(User.login == login, User.id != user.id))
        if existing:
            return False, "Такой логин уже занят."

        if len(login.strip()) < 3:
            return False, "Логин должен быть не короче 3 символов."

        if len(password) < 6:
            return False, "Пароль должен быть не короче 6 символов."

        user.login = login.strip()
        user.password_hash = pwd_context.hash(password)
        user.is_registered = True
        return True, "Регистрация успешно завершена."

    def login(self, db: Session, login: str, password: str) -> tuple[bool, User | None, str]:
        user = db.scalar(select(User).where(User.login == login.strip()))
        if not user or not user.password_hash:
            return False, None, "Пользователь не найден."

        if not pwd_context.verify(password, user.password_hash):
            return False, None, "Неверный пароль."

        return True, user, "Вход выполнен успешно."

    def accept_personal_data(self, user: User) -> None:
        user.personal_data_accepted = True
