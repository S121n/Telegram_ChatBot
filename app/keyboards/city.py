from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.utils.iran_locations import IRAN_PROVINCES


def city_keyboard(province: str):
    cities = IRAN_PROVINCES.get(province, [])

    buttons = []
    row = []

    for city in cities:
        row.append(KeyboardButton(text=city))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
