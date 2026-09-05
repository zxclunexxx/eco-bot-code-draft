from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import QuizSession, User
from src.integrations.ai import AIClient


class QuizService:
    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client or AIClient()

    def start_question(self, db: Session, user: User) -> tuple[QuizSession, list[str]]:
        question = self.ai_client.generate_quiz_question()
        correct_answer = question.options[question.correct_index]

        session = QuizSession(
            user_id=user.id,
            question=question.question,
            correct_answer=correct_answer,
            explanation=question.explanation,
            status="active",
        )
        db.add(session)
        db.flush()

        return session, question.options

    def get_active_session(self, db: Session, user: User) -> QuizSession | None:
        return db.scalar(
            select(QuizSession)
            .where(QuizSession.user_id == user.id, QuizSession.status == "active")
            .order_by(QuizSession.created_at.desc())
        )

    def check_text_answer(self, db: Session, user: User, answer_text: str) -> dict:
        session = self.get_active_session(db, user)
        if not session:
            return {
                "ok": False,
                "message": "Активная викторина не найдена. Нажмите «Викторина», чтобы начать.",
            }

        is_correct, ai_explanation = self.ai_client.check_answer(session.correct_answer, answer_text)

        if is_correct:
            user.points += 1
            user.correct_answers += 1
            result_text = f"Ответ верный. +1 очко\nВаши очки: {user.points}"
        else:
            user.points -= 1
            user.wrong_answers += 1
            result_text = (
                f"Ответ неверный. -1 очко\n"
                f"{session.explanation or ai_explanation}\n"
                f"Ваши очки: {user.points}"
            )

        session.status = "answered"
        return {
            "ok": True,
            "is_correct": is_correct,
            "message": result_text,
        }

    def finish(self, db: Session, user: User) -> None:
        sessions = db.scalars(
            select(QuizSession)
            .where(QuizSession.user_id == user.id, QuizSession.status.in_(["active", "answered"]))
        ).all()
        for session in sessions:
            session.status = "finished"
