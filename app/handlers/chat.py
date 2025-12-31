from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.database import get_db
from app.utils.active_chats import active_chats

router = Router()


# ================== KEYBOARDS ==================

chat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 مشاهده پروفایل")],
        [KeyboardButton(text="🚫 ریپورت"), KeyboardButton(text="❌ پایان چت")]
    ],
    resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 شروع چت ناشناس")],
        [KeyboardButton(text="👤 پروفایل من")]
    ],
    resize_keyboard=True
)


# ================== END CHAT (❗ اول از همه) ==================

@router.message(F.text == "❌ پایان چت")
async def end_chat(message: Message):
    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if not partner_id:
        await message.answer(
            "❌ چت فعالی وجود ندارد.",
            reply_markup=main_keyboard
        )
        return

    # حذف برای هر دو طرف
    active_chats.pop(user_id, None)
    active_chats.pop(partner_id, None)

    # اطلاع به طرف مقابل
    try:
        await message.bot.send_message(
            chat_id=partner_id,
            text="❌ مخاطب چت را پایان داد.",
            reply_markup=main_keyboard
        )
    except:
        pass

    await message.answer(
        "❌ چت با موفقیت پایان یافت.",
        reply_markup=main_keyboard
    )


# ================== VIEW PROFILE ==================

@router.message(F.text == "👤 مشاهده پروفایل")
async def show_partner_profile(message: Message):
    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if not partner_id:
        await message.answer("❌ مخاطبی برای نمایش پروفایل وجود ندارد.")
        return

    db = await get_db()
    db.row_factory = lambda cursor, row: dict(zip([c[0] for c in cursor.description], row))

    async with db.execute(
        """
        SELECT name, gender, age, province, city, profile_pic
        FROM users
        WHERE telegram_id = ?
        """,
        (partner_id,)
    ) as cursor:
        user = await cursor.fetchone()

    await db.close()

    if not user:
        await message.answer("❌ پروفایل مخاطب یافت نشد.")
        return

    text = (
        f"👤 <b>پروفایل مخاطب</b>\n\n"
        f"🔹 نام: {user['name']}\n"
        f"🔹 جنسیت: {user['gender']}\n"
        f"🔹 سن: {user['age']}\n"
        f"📍 {user['province']} - {user['city']}"
    )

    if user["profile_pic"]:
        await message.answer_photo(user["profile_pic"], caption=text)
    else:
        await message.answer(text)


# ================== RELAY MESSAGE (❗ آخر از همه) ==================

@router.message(F.text)
async def relay_message(message: Message):
    user_id = message.from_user.id

    # فقط اگر کاربر در چت است
    if user_id not in active_chats:
        return

    partner_id = active_chats.get(user_id)
    if not partner_id:
        return

    await message.bot.send_message(
        chat_id=partner_id,
        text=message.text
    )

