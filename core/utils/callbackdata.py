from aiogram.filters.callback_data import CallbackData


class Roadmap(CallbackData, prefix="roadmap"):
    id: int


class Quizze(CallbackData, prefix="quizze"):
    id: int


class QuizzeKnow(CallbackData, prefix="quizze_know"):
    id: int
    current: int


class QuizzeDidntKnow(CallbackData, prefix="quizze_didnt_know"):
    id: int
    current: int
