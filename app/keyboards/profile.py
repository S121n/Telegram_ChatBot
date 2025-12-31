from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ ویرایش نام", callback_data="edit_name")],
        [InlineKeyboardButton(text="📍 ویرایش استان", callback_data="edit_province")],
        [InlineKeyboardButton(text="🏙 ویرایش شهر", callback_data="edit_city")],
        [InlineKeyboardButton(text="🎂 ویرایش سن", callback_data="edit_age")],
        [InlineKeyboardButton(text="🖼 ویرایش عکس", callback_data="edit_photo")]
    ])
