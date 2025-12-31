from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiosqlite

from app.database import get_db
from app.services.matcher import active_chats  # ✅ اصلاح شده

router = Router()

# ================== KEYBOARDS ==================

chat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 مشاهده پروفایل")],
        [KeyboardButton(text="🚫 ریپورت"), KeyboardButton(text="❌ اتمام چت")]
    ],
    resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 اتصال ناشناس")],
        [KeyboardButton(text="👤 پروفایل من"), KeyboardButton(text="🎯 جستجوی ویژه")],
        [KeyboardButton(text="💰 خرید سکه"), KeyboardButton(text="🎁 دعوت دوستان")]
    ],
    resize_keyboard=True
)


# ================== END CHAT ==================

@router.message(F.text == "❌ اتمام چت")
async def end_chat(message: Message):
    """پایان دادن به چت فعال"""
    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if not partner_id:
        await message.answer(
            "❌ چت فعالی وجود ندارد.",
            reply_markup=main_keyboard
        )
        return


    active_chats.pop(user_id, None)
    active_chats.pop(partner_id, None)


    await message.answer(
        "❌ چت با موفقیت پایان یافت.",
        reply_markup=main_keyboard
    )


    try:
        await message.bot.send_message(
            chat_id=partner_id,
            text="❌ مخاطب چت را پایان داد.",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در ارسال پیام به partner: {e}")


# ================== VIEW PROFILE ==================

@router.message(F.text == "👤 مشاهده پروفایل")
async def show_partner_profile(message: Message):
    """نمایش پروفایل مخاطب"""
    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if not partner_id:
        await message.answer(
            "❌ مخاطبی برای نمایش پروفایل وجود ندارد.",
            reply_markup=chat_keyboard
        )
        return

    try:
        db = await get_db()


        db.row_factory = aiosqlite.Row

        async with db.execute(
                """
                SELECT name, gender, age, province, city, profile_pic
                FROM users
                WHERE telegram_id = ?
                """,
                (partner_id,)
        ) as cursor:
            row = await cursor.fetchone()

        await db.close()

        if not row:
            await message.answer(
                "❌ پروفایل مخاطب یافت نشد.",
                reply_markup=chat_keyboard
            )
            return


        user = dict(row)


        gender_fa = "پسر" if user['gender'] == "پسر" else "دختر"

        text = (
            f"👤 <b>پروفایل مخاطب</b>\n\n"
            f"🔹 نام: {user['name']}\n"
            f"🔹 جنسیت: {gender_fa}\n"
            f"🔹 سن: {user['age']} سال\n"
            f"📍 {user['province']} - {user['city']}"
        )


        if user.get("profile_pic"):
            await message.answer_photo(
                photo=user["profile_pic"],
                caption=text,
                parse_mode="HTML"
            )
        else:
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        print(f"خطا در نمایش پروفایل: {e}")
        await message.answer(
            "❌ خطا در دریافت اطلاعات پروفایل.",
            reply_markup=chat_keyboard
        )


# ================== RELAY MESSAGE  ==================

@router.message(F.text)
async def relay_message(message: Message):
    """ارسال پیام به مخاطب چت"""
    user_id = message.from_user.id


    if user_id not in active_chats:
        return

    partner_id = active_chats.get(user_id)

    if not partner_id:
        return

    try:
        await message.bot.send_message(
            chat_id=partner_id,
            text=message.text
        )
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")
        await message.answer("❌ خطا در ارسال پیام.")