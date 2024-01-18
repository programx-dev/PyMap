from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram.fsm.storage.redis import RedisStorage
import asyncio


class TrottlingMiddlware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = f"user{event.from_user.id}"

        check_user = await self.storage.redis.get(name=user)

        if check_user:
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value=0, ex=2)
                msg = await event.answer(f"Мы обнаружили подозрительную активность. Ждите 2 секунды")
                await asyncio.sleep(1)
                await msg.delete()
                return
            return
        await self.storage.redis.set(name=user, value=1, ex=2)

        return await handler(event, data)
