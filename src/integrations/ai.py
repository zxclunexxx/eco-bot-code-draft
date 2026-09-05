import random
from dataclasses import dataclass


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class AIClient:
    """Заглушка нейросети.

    В MVP можно работать без внешнего API.
    Позже методы можно заменить на вызовы реальной LLM.
    """

    def generate_quiz_question(self) -> QuizQuestion:
        questions = [
            QuizQuestion(
                question="Что нельзя выбрасывать в обычный мусор?",
                options=["Батарейки", "Бумажный пакет", "Картонную коробку", "Стеклянную банку"],
                correct_index=0,
                explanation="Батарейки содержат вещества, которые могут загрязнять почву и воду.",
            ),
            QuizQuestion(
                question="Что лучше сделать с пластиковой бутылкой перед сдачей в переработку?",
                options=["Наполнить водой", "Промыть и сжать", "Покрасить", "Разрезать на мелкие части"],
                correct_index=1,
                explanation="Чистая и сжатая бутылка занимает меньше места и проще сортируется.",
            ),
            QuizQuestion(
                question="Какой вариант помогает уменьшить количество одноразового пластика?",
                options=["Покупать больше пакетов", "Использовать многоразовую бутылку", "Смешивать отходы", "Выбрасывать всё в один контейнер"],
                correct_index=1,
                explanation="Многоразовые вещи заменяют одноразовые и уменьшают объём мусора.",
            ),
        ]
        return random.choice(questions)

    def check_answer(self, correct_answer: str, user_answer: str) -> tuple[bool, str]:
        normalized_correct = correct_answer.strip().lower()
        normalized_user = user_answer.strip().lower()
        is_correct = normalized_correct == normalized_user
        if is_correct:
            return True, "Ответ совпадает с правильным вариантом."
        return False, f"Правильный ответ: {correct_answer}."
