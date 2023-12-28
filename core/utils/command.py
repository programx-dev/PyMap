from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="📜 Справка бота"
        ),
        BotCommand(
            command="roadmap",
            description="🗺️ Дорожная карта"
        ),
        BotCommand(
            command="quizze",
            description="📝 Тестирование"
        ),
        BotCommand(
            command="cancel",
            description="↩️ Отмена"
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
