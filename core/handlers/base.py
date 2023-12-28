from aiogram import Bot
from aiogram.types import Message
from core.keyboards import inline
from core.utils.dbconnect import Request


async def get_start(message: Message, bot: Bot, request: Request):
    await request.add_data(message.from_user.id, message.from_user.first_name)
    await message.delete()

    description, file_id = (await request.get_dataroadmap(id=1))[2:4]

    await message.answer_photo(photo=file_id, caption=description, reply_markup=inline.intline_keyboard_start)


async def get_roadmap(message: Message, bot: Bot, request: Request):
    await message.delete()

    description, file_id, children, file_type = (await request.get_dataroadmap(id=2))[2:]

    kwargs = {"caption": description, "reply_markup": await inline.get_inline_keyboard_roadmap(children=children, request=request)}
    match file_type:
        case "photo":
            await message.answer_photo(file_id, **kwargs)
        case "document":
            await message.answer_document(file_id, **kwargs)


async def get_quizze(message: Message, bot: Bot, request: Request):
    await message.delete()

    children = (await request.get_quizze(id=1))[3]

    await message.answer(text="Выберите тест для его прохождения 📝",
                         reply_markup=await inline.get_inline_keyboard_quizzes(children=children, request=request))


async def nothing_cancel(message: Message, bot: Bot, request: Request):
    await message.delete()
    await message.answer(text="Активной команды для отмены нет")
