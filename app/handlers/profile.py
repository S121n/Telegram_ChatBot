from aiogram import Router, F
from aiogram.types import Message

from app.database import get_db

router = Router()


@router.message(F.text == "👤 پروفایل من")
async def my_profile(message: Message):
    db = await get_db()

    async with db.execute(
        """
        SELECT name, gender, age, province, city, coins, profile_pic
        FROM users
        WHERE telegram_id = ?
        """,
        (message.from_user.id,)
    ) as cursor:
        user = await cursor.fetchone()

    await db.close()

    if not user:
        await message.answer("❌ پروفایلی یافت نشد.")
        return

    text = (
        f"👤 <b>پروفایل شما</b>\n\n"
        f"🔹 نام: {user['name']}\n"
        f"🔹 جنسیت: {user['gender']}\n"
        f"🔹 سن: {user['age']}\n"
        f"📍 {user['province']} - {user['city']}\n"
        f"💰 سکه: {user['coins']}"
    )

    # =========================
    # اگر عکس پروفایل دارد
    # =========================
    if user["profile_pic"]:
        await message.answer_photo(
            photo=user["profile_pic"],
            caption=text
        )
    else:
        await message.answer(text)
