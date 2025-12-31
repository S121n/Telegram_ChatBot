from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

chat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ اتمام چت")],
        [KeyboardButton(text="👤 مشاهده پروفایل")]
    ],
    resize_keyboard=True
)
