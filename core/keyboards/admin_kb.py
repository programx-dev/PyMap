from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="/sender")
    ]
], resize_keyboard=True, one_time_keyboard=True, selective=True)
