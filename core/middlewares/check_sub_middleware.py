from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline_kb import get_inline_sub_channel
from core.utils.dbconnect import Request


def check_sub(chat_member: dict) -> bool:
    if chat_member.status != "left":
        return True

    return False


class CheckSubMiddleware(BaseMiddleware):
    def __init__(self, channel_id: str, channel_link: str, request: Request):
        super().__init__()
        self.channel_id = channel_id
        self.channel_link = channel_link
        self.request = request

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if check_sub(await data["bot"].get_chat_member(chat_id=self.channel_id,
                                                       user_id=int(data["event_from_user"].id))):
            return await handler(event, data)

        text = (await self.request.get_data_roadmap(0))[2]

        if isinstance(event, Message):
            if data["command"].command == "start":
                return await handler(event, data)

            await event.reply(text, reply_markup=get_inline_sub_channel(self.channel_link), disable_web_page_preview=True)

        elif isinstance(event, CallbackQuery):
            if event.data == "check_sub_channel":
                return await handler(event, data)

            await event.message.answer(text, reply_markup=get_inline_sub_channel(self.channel_link), disable_web_page_preview=True)
            await event.answer()
