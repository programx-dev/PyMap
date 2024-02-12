from aiogram import Bot
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import Message
from core.keyboards import inline_kb
from core.utils.dbconnect import Request


def check_sub(chat_member: dict) -> bool:
    if chat_member.status != "left":
        return True

    return False


async def get_start(message: Message, bot: Bot, request: Request, channel_id: str):
    await message.delete()

    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot, initial_sleep=0.5):
        await request.add_data_user(message.from_user.id, message.from_user.first_name)

        description, file_id = (await request.get_data_roadmap(id=1))[2:4]

        await message.answer_photo(photo=file_id, caption=description, reply_markup=inline_kb.intline_keyboard_start)

        if not check_sub(await bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)):
            await message.answer(text=(await request.get_data_roadmap(id=0))[2])


async def get_roadmap(message: Message, bot: Bot, request: Request):
    await message.delete()

    description, file_id, children, file_type = (await request.get_data_roadmap(id=2))[2:]

    kwargs = {"caption": description, "reply_markup": await inline_kb.get_inline_keyboard_roadmap(children=children, request=request)}
    match file_type:
        case "photo":
            await message.answer_photo(file_id, **kwargs)
        case "document":
            await message.answer_document(file_id, **kwargs)


async def get_lst_test(message: Message, bot: Bot, request: Request):
    await message.delete()

    children = (await request.get_data_test(id=1))[3]

    await message.answer(text="Выберите тест для его прохождения 📝",
                         reply_markup=await inline_kb.get_inline_keyboard_lst_test(children=children, request=request))


async def get_lst_quizze(message: Message, bot: Bot, request: Request):
    await message.delete()

    await message.answer(text="Выберите задачу для её прохождения 🧩",
                         reply_markup=await inline_kb.get_inline_keyboard_lst_quizze(offset=0,
                                                                                  user_id=message.from_user.id,
                                                                                  request=request))


async def nothing_cancel(message: Message, bot: Bot, request: Request):
    await message.delete()
    await message.answer(text="Активной команды для отмены нет")
