from aiogram.filters.callback_data import CallbackData


class Roadmap(CallbackData, prefix="roadmap"):
    id: int


class Test(CallbackData, prefix="test"):
    id: int


class Quizze(CallbackData, prefix="quizze"):
    id: int


class QuizzeBack(CallbackData, prefix="quizze_back"):
    offset: int


class QuizzeForward(CallbackData, prefix="quizze_forward"):
    offset: int


class TestKnow(CallbackData, prefix="test_know"):
    id: int
    current: int


class TestNotKnow(CallbackData, prefix="test_not_know"):
    id: int
    current: int
