import logging
from aiogram import Bot, Dispatcher, F
from aiogram.methods import DeleteWebhook
import asyncio
from core.settings import settings
from aiogram.filters import Command
from core.utils.command import set_commands
from core.handlers import base
from core.utils import callbackdata
from core.middlewares.dbmiddleware import DbSession
from core.utils import statequizze
from core.handlers import quizze
from core.handlers import callback
from core.handlers import admin
import asyncpg

# "%(asctime)s - [%(levelname)s] - %(name)s"
# "%(filename)s - %(funcName)s(%(lineno)d) -  %(message)s"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - (%(filename)s), line %(lineno)d - %(message)s")


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text="Бот запущен!")


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")


async def create_pool():
    logging.info("Успешное соединение с БД!")
    return await asyncpg.create_pool(user="postgres", password="777", database="roadmap",
                                     host="127.0.0.1", port=5432, command_timeout=60)


async def start():
    bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
    pool_connect = await create_pool()
    dp = Dispatcher()

    dp.update.middleware.register(DbSession(pool_connect))

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.callback_query.register(quizze.init_quizze, callbackdata.Quizze.filter())
    dp.callback_query.register(quizze.get_quizze, statequizze.StepsQuizze.GET_QUZZE,
                               F.data.in_({"know", "dont_know"}))
    dp.callback_query.register(quizze.get_answer_quizze, statequizze.StepsQuizze.GET_QUZZE,
                               F.data.in_({"show_answer", "show_question"}))
    dp.message.register(quizze.get_stop_confirm, statequizze.StepsQuizze.GET_QUZZE, Command(commands="cancel"))
    dp.callback_query.register(quizze.stop_test, statequizze.StepsQuizze.GET_QUZZE, F.data.in_({"stop_test", "cancel"}))
    dp.message.register(quizze.get_ignore, statequizze.StepsQuizze.GET_QUZZE)

    dp.message.register(admin.get_photo_id, F.photo, F.from_user.id == settings.bots.admin_id)
    dp.message.register(admin.get_document_id, F.document, F.from_user.id == settings.bots.admin_id)

    dp.callback_query.register(callback.delete_msg, F.data == "delete")
    dp.callback_query.register(callback.get_roadmap, callbackdata.Roadmap.filter())

    dp.message.register(base.get_start, Command(commands="start"))
    dp.message.register(base.get_roadmap, Command(commands="roadmap"))
    dp.message.register(base.get_quizze, Command(commands="quizze"))
    dp.message.register(base.nothing_cancel, Command(commands="cancel"))

    try:
        logging.warning("Бот запущен!")
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logging.warning("Бот остановлен!")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())
