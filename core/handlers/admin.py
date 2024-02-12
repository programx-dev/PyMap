from aiogram.types import Message
from aiogram import Bot

async def get_photo_id(message: Message, bot: Bot):
    await message.answer(f"Ты отправил мне картинку, вот её ID: <code>{message.photo[-1].file_id}</code>")

async def get_document_id(message: Message, bot: Bot):
    await message.answer(f"Ты отправил мне кокумент, вот его ID: <code>{message.document.file_id}</code>")
