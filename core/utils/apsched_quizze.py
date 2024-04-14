from aiogram import Bot
from core.utils.dbconnect import Request
from core.utils.sender_quizze import SenderList



async def send_message_cron(bot: Bot, id_admin: int, sender_quizze: SenderList, request: Request):
    await bot.send_message(id_admin, "Начинаю рассылку задач")

    name_camp = "quizze_sending"

    if not await request.check_table(name_camp):
        await request.create_table(name_camp)

    count = await sender_quizze.broadcaster(name_camp)

    await bot.send_message(id_admin, f"Успешно разослал задачи {count} пользовательям")
    await request.delete_table(name_camp)
