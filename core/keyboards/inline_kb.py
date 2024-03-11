from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.utils import callbackdata
from core.utils.dbconnect import Request

def get_inline_sub_channel(url: str):
    inline_sub_channel = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Подписаться",
                url=url
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Проверить подписку",
                callback_data="check_sub_channel"
            )
        ]
    ])

    return inline_sub_channel


def get_inline_keyboard_start(url: str):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="🗺️ Дорожная карта", callback_data=callbackdata.Roadmap(id=2))
    keyboard_builder.button(text="💬 Оставить отзыв", url=url)

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_roadmap(children: list[str], request: Request):
    keyboard_builder = InlineKeyboardBuilder()

    for id in children:
        name = (await request.get_data_roadmap(id=id))[1]
        keyboard_builder.button(text=name, callback_data=callbackdata.Roadmap(id=id))

    keyboard_builder.button(text="Удалить", callback_data="delete")

    tmp = [2] * (len(children) // 2)

    if len(children) % 2 == 1:
        tmp.append(1)

    keyboard_builder.adjust(*tmp, 1)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_lst_test(children: list[str], request: Request):
    keyboard_builder = InlineKeyboardBuilder()

    for id in children:
        name = (await request.get_data_test(id=id))[1]
        keyboard_builder.button(text=name, callback_data=callbackdata.Test(id=id))

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_lst_quizze(offset: int, user_id: int, request: Request):
    max_id = await request.get_max_id_quizze()

    keyboard_builder = InlineKeyboardBuilder()

    correct_quizzes, wrong_quizzes = (await request.get_data_users(user_id=user_id))[2:]
    max_row = 4
    max_column = 4

    for id in range(start := offset * max_row * max_column, end := min(start + max_row * max_column, max_id)):
        text = str(id + 1)
        if id + 1 in correct_quizzes:
            text = f"✅ {text}"
        elif id + 1 in wrong_quizzes:
            text = f"❌ {text}"

        keyboard_builder.button(text=text, callback_data=callbackdata.Quizze(id=id + 1))

    row_count = max_row
    if offset == max_id // (max_row * max_column):
        row_count = (max_id % (max_row * max_column)) // max_column

    tmp = [max_column] * row_count

    if (end - start) % max_column != 0:
        tmp.append((end - start) % max_column)

    tool_btn = 0

    if offset != 0:
        keyboard_builder.button(text="⬅️ Назад", callback_data=callbackdata.QuizzeBack(offset=offset))
        tool_btn += 1

    if max_id > (offset + 1) * max_column * max_row:
        keyboard_builder.button(text="➡️ Вперед", callback_data=callbackdata.QuizzeForward(offset=offset))
        tool_btn += 1

    if tool_btn:
        tmp.append(tool_btn)

    keyboard_builder.adjust(*tmp)

    return keyboard_builder.as_markup()


async def get_inline_keyboard_test(show_answer: bool = True):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="✅ Уже знаю это", callback_data="know")
    keyboard_builder.button(text="📚 Не знаю это", callback_data="not_know")
    keyboard_builder.button(text="⏭ Пропустить", callback_data="skip")

    if show_answer:
        keyboard_builder.button(text="🔍 Показать ответ", callback_data="show_answer")
    else:
        keyboard_builder.button(text="❓ Показать вопрос", callback_data="show_question")

    keyboard_builder.adjust(3, 1)

    return keyboard_builder.as_markup()


async def get_stop_test():
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="🏁 Завершить тест", callback_data="stop_test")
    keyboard_builder.button(text="↩️ Отмена", callback_data="cancel")

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()


async def get_confirm_button_sender():
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="Добавить кнопку", callback_data="add_button")
    keyboard_builder.button(text="Продолжить без кнопки", callback_data="no_button")
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
