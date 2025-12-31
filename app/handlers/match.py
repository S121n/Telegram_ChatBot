from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.database import get_db
from app.services.matcher import (
    add_to_waiting, find_match, start_chat, is_in_chat
)
from app.keyboards.chat import chat_keyboard

router = Router()


@router.message(lambda m: m.text == "🔍 اتصال ناشناس")
async def start_match(message: Message):
    user_id = message.from_user.id

    if is_in_chat(user_id):
        await message.answer("❌ شما در حال حاضر در چت هستید.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="پسر"), KeyboardButton(text="دختر")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👫 می‌خواهید به چه جنسیتی وصل شوید؟",
        reply_markup=keyboard
    )


@router.message(lambda m: m.text in ["پسر", "دختر"])
async def select_target_gender(message: Message):
    target_gender = message.text
    user_id = message.from_user.id

    db = await get_db()
    async with db.execute(
        "SELECT gender, coins FROM users WHERE telegram_id = ?",
        (user_id,)
    ) as cursor:
        user = await cursor.fetchone()

    if not user:
        await db.close()
        await message.answer("❌ کاربر یافت نشد.")
        return

    if user["coins"] < 2:
        await db.close()
        await message.answer("❌ سکه کافی ندارید.")
        return

    user_data = {
        "id": user_id,
        "gender": user["gender"],
        "target_gender": target_gender
    }

    match = find_match(user_data)

    if match:
        await db.execute(
            "UPDATE users SET coins = coins - 2 WHERE telegram_id IN (?, ?)",
            (user_id, match["id"])
        )
        await db.commit()

        start_chat(user_id, match["id"])

        await message.answer("✅ مخاطب پیدا شد!", reply_markup=chat_keyboard)
        await message.bot.send_message(
            match["id"],
            "✅ مخاطب پیدا شد!",
            reply_markup=chat_keyboard
        )
    else:
        add_to_waiting(user_data)
        await message.answer("⏳ در حال جستجوی مخاطب...")

    await db.close()


@router.message()
async def relay_chat(message: Message):
    from app.services.matcher import active_chats

    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if partner_id:
        await message.bot.send_message(partner_id, message.text)
