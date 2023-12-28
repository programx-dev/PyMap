import asyncpg
import logging


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_data(self, user_id, user_name):
        query = f"INSERT INTO datausers (user_id, user_name) VALUES ({user_id}, '{user_name}')"\
                f"ON CONFLICT (user_id) DO UPDATE SET user_name='{user_name}'"
        await self.connector.execute(query)

    async def get_dataroadmap(self, id: int) -> list[int, str, str, str, list[int], str]:
        query = f"SELECT * FROM dataroadmap WHERE id={id}"
        return await self.connector.fetchrow(query)

    async def get_quizze(self, id: int) -> list[str, str, list[int]]:
        query = f"SELECT * FROM quizzes WHERE id={id}"
        return await self.connector.fetchrow(query)
