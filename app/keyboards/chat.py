from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

chat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 مشاهده پروفایل")],
        [KeyboardButton(text="🚫 ریپورت"), KeyboardButton(text="❌ اتمام چت")]
    ],
    resize_keyboard=True
)