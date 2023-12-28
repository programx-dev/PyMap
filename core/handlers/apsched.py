from aiogram import Bot


async def send_message_time(bot: Bot):
    await bot.send_message(5014277973, f"Это сообщение отправлено через несколько секунд после старта бота")


async def send_message_cron(bot: Bot):
    await bot.send_message(5014277973, f"Это сообщение будет отправлятся ежедневно в указанное время")


async def send_message_interval(bot: Bot):
    await bot.send_message(5014277973, f"Это сообщение будет отправлятся с интервалом в 1 минуту"
    
)
