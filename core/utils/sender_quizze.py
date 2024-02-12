from aiogram import Bot, Dispatcher
import asyncpg
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramRetryAfter
import asyncio
from core.utils.states import StepsQuizze
from core.utils.dbconnect import Request
from asyncpg.pool import Pool, PoolAcquireContext
from random import choice
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext
import logging


class SenderList:
    def __init__(self, bot: Bot, dp: Dispatcher, channel_id: str, request: Request):
        self.bot = bot
        self.dp = dp
        self.channel_id = channel_id
        self.request = request

    async def update_statuse(self, table_name, user_id, statuse, description):
        async with self.request.connector.acquire() as connect:
            query = f"UPDATE {table_name} SET statuse='{statuse}', description='{description}' WHERE user_id={user_id};"
            await connect.execute(query)

    async def get_count_users(self, name_camp):
        async with self.request.connector.acquire() as connect:
            query = f"CREATE INDEX IF NOT EXISTS {name_camp}_idx  ON {name_camp}(user_id);"
            await connect.execute(query)
            query = f"SELECT reltuples::bigint AS estimate FROM pg_class where relname = '{name_camp}_idx';"
            return await connect.fetchval(query)

    async def get_portion_users(self, name_camp, offset, rows):
        async with self.request.connector.acquire() as connect:
            query = f"SELECT * FROM {name_camp} WHERE statuse = 'waiting' ORDER BY user_id OFFSET {offset} ROWS FETCH NEXT {rows} ROWS ONLY;"
            results_query: list[asyncpg.Record] = await connect.fetch(query)
            return [result.get("user_id") for result in results_query]

    async def get_users(self, name_camp):
        async with self.request.connector.acquire() as connect:
            query = f"SELECT user_id FROM {name_camp} WHERE statuse = 'waiting';"
            results_query: list[asyncpg.Record] = await connect.fetch(query)
            return [result.get("user_id") for result in results_query]

    async def send_message(self, name_camp: str, user_id: int, quizze_id: int):
        try:
            user_storage_key = StorageKey(self.bot.id, user_id, user_id) 
            user_context = FSMContext(storage=self.dp.storage, key=user_storage_key)

            await user_context.set_state(StepsQuizze.QUIZZE)

            question, answers, photo_id, solution, correct_answer = (await self.request.get_data_quizze(quizze_id))[1:]

            await self.bot.send_photo(user_id, photo=photo_id, disable_notification=True)
            poll = await self.bot.send_poll(user_id, question=f"#{quizze_id} {question}", options=answers, type="quiz",
                                            correct_option_id=correct_answer, explanation=solution, is_anonymous=False, 
                                            disable_notification=True)

            await user_context.update_data(poll_id=poll.poll.id)
            await user_context.update_data(quizze_id=quizze_id)
            await user_context.update_data(correct_answer=correct_answer)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            return await self.send_message(name_camp, user_id, quizze_id)
        except Exception as e:
            await self.update_statuse(name_camp, user_id, "unsuccessful", f"{e}")
        else:
            await self.update_statuse(name_camp, user_id, "successful", "No errors")
            return True

        return False

    async def get_quizze_id(self, user_id: int):
        async with self.request.connector.acquire() as connect:
            connect: Pool
            query = f"SELECT id FROM quizzes;"
            all_quizzes: list[asyncpg.Record] = await connect.fetch(query)
            all_quizzes = {result.get("id") for result in all_quizzes}

            query = f"SELECT correct_quizzes FROM users WHERE user_id = {user_id};"
            correct_quizzes = set(await connect.fetchval(query))

            quizzes = list(all_quizzes - correct_quizzes)

            if len(quizzes) == 0:
                return None

            quizze_id = choice(list(quizzes))

            return quizze_id

    def check_sub(self, chat_member: dict) -> bool:
        if chat_member.status != "left":
            return True

        return False

    async def broadcaster(self, name_camp: str):
        users_ids = await self.get_users(name_camp)
        count = 0

        try:
            for user_id in users_ids:
                if self.check_sub(await self.bot.get_chat_member(chat_id=self.channel_id, user_id=user_id)):
                    quizze_id = await self.get_quizze_id(int(user_id))

                    if quizze_id != None:
                        if await self.send_message(name_camp, int(user_id), quizze_id):
                            count += 1
                        await asyncio.sleep(.04)
        finally:
            logging.info(f"Успешно разослал задачи {count} пользователям")

        return count
