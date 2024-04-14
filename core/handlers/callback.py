from aiogram import Bot
from aiogram.types import CallbackQuery
from core.utils import callbackdata
from core.utils.dbconnect import Request
from core.keyboards.inline_kb import get_inline_keyboard_roadmap
from core.keyboards import inline_kb


async def delete_msg(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


async def check_sub_channel(call: CallbackQuery, bot: Bot, channel_id: str):
    if (await bot.get_chat_member(chat_id=channel_id, user_id=call.from_user.id)).status == "left":
        await call.answer(text="❌ Вы не подписались на канал!", show_alert=True)
        return

    await call.answer(text="✅ Спасибо за подписку! Теперь вы можете пользоваться ботом!")

    await call.message.delete()


async def set_settings(call: CallbackQuery, callback_data: callbackdata.Settings, request: Request):
    await request.set_user_settings(
        user_id=call.from_user.id,
        user_name=call.from_user.first_name,
        newsletter=not (callback_data.newsletter)
    )

    settings = (await request.get_data_users(user_id=call.from_user.id))[4:]

    await call.message.edit_reply_markup(reply_markup=inline_kb.get_inline_keyboard_settings(settings))


async def get_roadmap(call: CallbackQuery, callback_data: callbackdata.Roadmap, request: Request):
    id = callback_data.id
    name, description, file_id, children, file_type = (await request.get_data_roadmap(id=id))[1:]

    message = f"<b>{name}</b>\n\n{description}"

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


async def get_lst_quizze_back(call: CallbackQuery, callback_data: callbackdata.QuizzeBack, request: Request):
    await call.message.edit_reply_markup(
        reply_markup=await inline_kb.get_inline_keyboard_lst_quizze(offset=callback_data.offset - 1,
                                                                    user_id=call.from_user.id,
                                                                    request=request))

    await call.answer()


async def get_lst_quizze_forward(call: CallbackQuery, callback_data: callbackdata.QuizzeBack, request: Request):
    await call.message.edit_reply_markup(
        reply_markup=await inline_kb.get_inline_keyboard_lst_quizze(offset=callback_data.offset + 1,
                                                                    user_id=call.from_user.id,
                                                                    request=request))

    await call.answer()
