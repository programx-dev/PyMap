from aiogram import Bot
from aiogram.types import CallbackQuery
from core.utils import callbackdata
from core.utils.dbconnect import Request
from core.keyboards.inline import get_inline_keyboard_roadmap
from aiogram.utils.chat_action import ChatActionSender
from core.keyboards import inline


async def delete_msg(call: CallbackQuery, bot: Bot):
    await call.message.delete()
    await call.answer()


async def check_sub_cannel(call: CallbackQuery, bot: Bot, channel_id: str):
    if (await bot.get_chat_member(chat_id=channel_id, user_id=call.from_user.id)).status == "left":
        await call.answer(text="❌ Вы не подписались на канал!", show_alert=True)
        return

    await call.answer(text="✅ Спасибо за подписку! Теперь вы можете пользоваться ботом!")
    await call.message.delete()


async def get_roadmap(call: CallbackQuery, bot: Bot, callback_data: callbackdata.Roadmap, request: Request):
    id = callback_data.id
    name, description, file_id, children, file_type = (await request.get_data_roadmap(id=id))[1:]

    message = f"<b>{name}</b>\n\n{description}"

    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    if file_id:
        kwargs = {"caption": message, "reply_markup": await get_inline_keyboard_roadmap(children=children, request=request)}
        match file_type:
            case "photo":
                await call.message.answer_photo(file_id, **kwargs)
            case "document":
                await call.message.answer_document(file_id, **kwargs)
    else:
        await call.message.answer(text=message, reply_markup=await get_inline_keyboard_roadmap(children=children, request=request))

    await call.answer()


async def get_lst_quizze_back(call: CallbackQuery, bot: Bot, callback_data: callbackdata.QuizzeBack, request: Request):
    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    await call.message.edit_reply_markup(reply_markup=await inline.get_inline_keyboard_lst_quizze(offset=callback_data.offset - 1,
                                                                                    user_id=call.from_user.id,
                                                                                    request=request))

    await call.answer()


async def get_lst_quizze_forward(call: CallbackQuery, bot: Bot, callback_data: callbackdata.QuizzeBack, request: Request):
    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    await call.message.edit_reply_markup(reply_markup=await inline.get_inline_keyboard_lst_quizze(offset=callback_data.offset + 1,
                                                                                        user_id=call.from_user.id,
                                                                                        request=request))

    await call.answer()
