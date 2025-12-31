from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.utils.iran_locations import IRAN_PROVINCES


def province_keyboard():
    buttons = []

    row = []
    for province in IRAN_PROVINCES.keys():
        row.append(KeyboardButton(text=province))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
