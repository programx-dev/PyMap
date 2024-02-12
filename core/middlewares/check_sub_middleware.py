from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline_kb import inline_sub_channel


def check_sub(chat_member: dict) -> bool:
    if chat_member.status != "left":
        return True

    return False


class CheckSubMiddlewareMessage(BaseMiddleware):
    def __init__(self, channel_id: str):
        super().__init__()
        self.channel_id = channel_id

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if data["command"].command == "start" or check_sub(await data["bot"].get_chat_member(chat_id=self.channel_id,
                                                                                             user_id=int(data["event_from_user"].id))):
            return await handler(event, data)

        await event.reply("❗️ Для того, чтобы воспользоваться ботом, пожалуйста подпишитесь на канал 👇", reply_markup=inline_sub_channel)


class CheckSubMiddlewareCallback(BaseMiddleware):
    def __init__(self, channel_id: str):
        super().__init__()
        self.channel_id = channel_id

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if event.data == "check_sub_channel" or check_sub(await data["bot"].get_chat_member(chat_id=self.channel_id,
                                                       user_id=int(data["event_from_user"].id))):
            return await handler(event, data)

        await event.message.reply("❗️ Для того, чтобы воспользоваться ботом, пожалуйста подпишитесь на канал 👇", reply_markup=inline_sub_channel)
        await event.answer()
