from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

coins_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 50 سکه - 25,000 تومان")],
        [KeyboardButton(text="💰 120 سکه - 50,000 تومان")],
        [KeyboardButton(text="💰 300 سکه - 100,000 تومان")],
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)
