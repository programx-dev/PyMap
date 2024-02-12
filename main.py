import asyncio
import asyncpg
from datetime import datetime
import logging
import contextlib
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.methods import DeleteWebhook
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.settings import settings
from core.utils.command import set_commands
from core.utils import apsched_quizze, callbackdata, sender_list, sender_quizze, states, sender_state, rolling_gzip_file
from core.utils.dbconnect import Request
from core.middlewares.db_middleware import DbSession
from core.middlewares import trottling_middleware  # check_sub_middleware
from core.handlers import test, quizze, callback, admin, base, sender
from core.keyboards import admin_kb


file_handler = rolling_gzip_file.RollingGzipFileHandler(f"logs/{__name__}.log", mode="a", encoding="utf-8",
                                      maxBytes=10485760)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s,%(msecs)03d %(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) %(message)s",
                    datefmt="%m/%d/%Y %H:%M:%S",
                    handlers=[file_handler, stream_handler])

logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logging.getLogger("aiogram.utils.chat_action").setLevel(logging.INFO)

# "%(asctime)s - [%(levelname)s] - (%(filename)s), line %(lineno)d - %(message)s"
# "%(name)s (%(filename)s) (%(asctime)s,%(msecs)03d) [%(levelname)s] :%(lineno)d - %(message)s"


def excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    logging.error("Неперехваченное исключение", exc_info=(exc_type, exc_value, exc_tb))

    # "".join(traceback.format_exception(exc_type, exc_value, exc_tb))


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text="Бот запущен!", reply_markup=admin_kb.admin_kb)


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")


async def create_pool():
    logging.info("Успешное соединение с БД!")
    return await asyncpg.create_pool(user="postgres", password="777", database="roadmap",
                                     host="127.0.0.1", port=5432, command_timeout=60)


async def start():
    bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
    pool_connect = await create_pool()
    storage = RedisStorage.from_url("redis://localhost:6379/0")
    dp = Dispatcher(storage=storage)

    sender_quizze_ = sender_quizze.SenderList(bot, dp, settings.channel_id, Request(pool_connect))

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(apsched_quizze.send_message_cron, trigger="cron", hour=13, start_date=datetime.now(),
                      kwargs={"bot": bot, "id_admin": settings.bots.admin_id, "sender_quizze": sender_quizze_, "request": Request(pool_connect)})
    # scheduler.add_job(apsched.send_message_cron, trigger="cron", hour=datetime.now().hour, minute=datetime.now().minute + 1, start_date=datetime.now(),
    #                   kwargs={"bot": bot, "id_admin": settings.bots.admin_id, "sender_quizze": sender_quizze_, "request": Request(pool_connect)})
    scheduler.start()

    # :TODO отправлять в 13:00 # datetime.hour(13)
    #  hour=datetime.now().hour,
    #   minute=datetime.now().minute + 1,

    dp.update.middleware.register(DbSession(pool_connect))
    # dp.message.middleware.register(check_sub_middleware.CheckSubMiddlewareMessage(settings.channel_id))
    # dp.callback_query.middleware.register(check_sub_middleware.CheckSubMiddlewareCallback(settings.channel_id))
    dp.message.middleware.register(trottling_middleware.TrottlingMiddlware(storage))

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.callback_query.register(test.init_test, callbackdata.Test.filter())
    dp.callback_query.register(test.get_test, states.StepsTest.TEST,
                               F.data.in_({"know", "not_know", "skip"}))
    dp.callback_query.register(test.get_answer_test, states.StepsTest.TEST,
                               F.data.in_({"show_answer", "show_question"}))
    dp.message.register(test.get_stop_confirm, states.StepsTest.TEST, Command(commands="cancel"))
    dp.callback_query.register(test.stop_test, states.StepsTest.TEST, F.data.in_({"stop_test", "cancel"}))
    dp.message.register(test.get_ignore, states.StepsTest.TEST)

    dp.callback_query.register(quizze.get_quizze, callbackdata.Quizze.filter())
    dp.callback_query.register(callback.get_lst_quizze_back, callbackdata.QuizzeBack.filter())
    dp.callback_query.register(callback.get_lst_quizze_forward, callbackdata.QuizzeForward.filter())
    dp.poll_answer.register(quizze.get_quizze_answer)

    dp.callback_query.register(callback.check_sub_channel, F.data == "check_sub_channel")

    dp.message.register(sender.get_sender, Command("sender"),  F.chat.id == settings.bots.admin_id)
    dp.message.register(sender.get_message, sender_state.Steps.get_message)
    dp.callback_query.register(sender.q_button, sender_state.Steps.q_button)
    dp.message.register(sender.get_text_button, sender_state.Steps.get_text_button)
    dp.message.register(sender.get_url_button, sender_state.Steps.get_url_button)
    dp.callback_query.register(sender.sender_decide, sender_state.Steps.sender_decide)

    dp.message.register(admin.get_photo_id, F.photo, F.from_user.id == settings.bots.admin_id)
    dp.message.register(admin.get_document_id, F.document, F.from_user.id == settings.bots.admin_id)

    dp.callback_query.register(callback.delete_msg, F.data == "delete")
    dp.callback_query.register(callback.get_roadmap, callbackdata.Roadmap.filter())

    dp.message.register(base.get_start, Command(commands="start"))
    dp.message.register(base.get_roadmap, Command(commands="roadmap"))
    dp.message.register(base.get_lst_test, Command(commands="test"))
    dp.message.register(base.get_lst_quizze, Command(commands="quizze"))
    dp.message.register(base.nothing_cancel, Command(commands="cancel"))

    sender_lst = sender_list.SenderList(bot, pool_connect)

    try:
        logging.warning("Бот запущен!")
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), sender_list=sender_lst, channel_id=settings.channel_id)
    except Exception as ex:
        logging.error(f"Неперехваченное исключение", exc_info=True)
    finally:
        logging.warning("Бот остановлен!")
        await bot.session.close()
        await dp.storage.close()

if __name__ == "__main__":
    sys.excepthook = excepthook

    with open(f"logs/{__name__}.log", mode="a", encoding="utf-8") as file:
        file.write(f"{datetime.now().strftime(' %m/%d/%Y %H:%M:%S '):=^100}\n")

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())
