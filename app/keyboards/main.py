from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 اتصال ناشناس")],
        [KeyboardButton(text="👤 پروفایل من"), KeyboardButton(text="🎯 جستجوی ویژه")],
        [KeyboardButton(text="💰 خرید سکه"), KeyboardButton(text="🎁 دعوت دوستان")]
    ],
    resize_keyboard=True
)
