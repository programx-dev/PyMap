from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.callbackdata import Roadmap, Quizze
from core.utils.dbconnect import Request

keyboard_builder = InlineKeyboardBuilder()
keyboard_builder.button(text="Дорожная карта", callback_data=Roadmap(id=2))
intline_keyboard_start = keyboard_builder.as_markup()


async def get_inline_keyboard_roadmap(children: list[str], request: Request):
    keyboard_builder = InlineKeyboardBuilder()

    for id in children:
        name = (await request.get_dataroadmap(id=id))[1]
        keyboard_builder.button(text=name, callback_data=Roadmap(id=id))

    keyboard_builder.button(text="❌ Удалить", callback_data="delete")

    tmp = [2] * (len(children) // 2)

    if len(children) % 2 == 1:
        tmp.append(1)

    keyboard_builder.adjust(*tmp, 1)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_quizzes(children: list[str], request: Request):
    keyboard_builder = InlineKeyboardBuilder()

    for id in children:
        name = (await request.get_quizze(id=id))[1]
        keyboard_builder.button(text=name, callback_data=Quizze(id=id))

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_question(show_answer: bool = True):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="✅ Уже знаю это", callback_data="know")
    keyboard_builder.button(text="📚 Не знаю это", callback_data="dont_know")

    if show_answer:
        keyboard_builder.button(text="🔍 Показать ответ", callback_data="show_answer")
    else:
        keyboard_builder.button(text="❓ Показать вопрос", callback_data="show_question")

    keyboard_builder.adjust(2, 1)

    return keyboard_builder.as_markup()


async def get_stop_test():
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="🏁 Завершить тест", callback_data="stop_test")
    keyboard_builder.button(text="↩️ Отмена", callback_data="cancel")

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()
