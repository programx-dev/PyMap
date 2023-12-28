from aiogram import Bot
from aiogram.types import CallbackQuery
from core.utils.callbackdata import Roadmap
from core.utils.dbconnect import Request
from core.keyboards.inline import get_inline_keyboard_roadmap


async def delete_msg(call: CallbackQuery, bot: Bot):
    await call.message.delete()
    await call.answer()


async def get_roadmap(call: CallbackQuery, bot: Bot, callback_data: Roadmap, request: Request):
    id = callback_data.id
    description, file_id, children, file_type = (await request.get_dataroadmap(id=id))[2:]

    if file_id:
        kwargs = {"caption": description, "reply_markup": await get_inline_keyboard_roadmap(children=children, request=request)}
        match file_type:
            case "photo":
                await call.message.answer_photo(file_id, **kwargs)
            case "document":
                await call.message.answer_document(file_id, **kwargs)
    else:
        await call.message.answer(text=description,
                                  reply_markup=await get_inline_keyboard_roadmap(children=children, request=request))

    await call.answer()



