from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.database import get_db
from app.services.matcher import (
    add_to_waiting, find_match, start_chat, is_in_chat
)
from app.keyboards.chat import chat_keyboard
from app.keyboards.main import main_keyboard

router = Router()


@router.message(lambda m: m.text == "🔍 اتصال ناشناس")
async def start_match(message: Message):
    """شروع فرآیند جستجوی مخاطب"""
    user_id = message.from_user.id

    # Check if the user is not currently in chat
    if is_in_chat(user_id):
        await message.answer(
            "❌ شما در حال حاضر در چت هستید.",
            reply_markup=chat_keyboard
        )
        return

    # Show gender selection keyboard
    gender_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="پسر"), KeyboardButton(text="دختر")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👫 می‌خواهید به چه جنسیتی وصل شوید؟",
        reply_markup=gender_keyboard
    )


@router.message(lambda m: m.text in ["پسر", "دختر"])
async def select_target_gender(message: Message):
    """انتخاب جنسیت مورد نظر برای چت"""
    target_gender = message.text
    user_id = message.from_user.id

    try:
        db = await get_db()

        # Get user information
        async with db.execute(
                "SELECT gender, coins FROM users WHERE telegram_id = ?",
                (user_id,)
        ) as cursor:
            user = await cursor.fetchone()

        if not user:
            await db.close()
            await message.answer(
                "❌ کاربر یافت نشد. لطفاً ابتدا ثبت‌نام کنید.",
                reply_markup=main_keyboard
            )
            return

        # Check coin balance
        if user[1] < 2:  # user[1] = coins
            await db.close()
            await message.answer(
                "❌ سکه کافی ندارید.\n\n"
                "💰 برای هر چت 2 سکه نیاز است.\n"
                "از منوی اصلی می‌توانید سکه خریداری کنید.",
                reply_markup=main_keyboard
            )
            return

        user_data = {
            "id": user_id,
            "gender": user[0],  # user[0] = gender
            "target_gender": target_gender
        }

        # Contact search
        match = find_match(user_data)

        if match:
            # Deduct coins from both users
            await db.execute(
                "UPDATE users SET coins = coins - 2 WHERE telegram_id IN (?, ?)",
                (user_id, match["id"])
            )
            await db.commit()

            # Start chat
            start_chat(user_id, match["id"])

            # Notify both users
            await message.answer(
                "✅ مخاطب پیدا شد!\n\n"
                "💬 می‌توانید شروع به چت کنید.",
                reply_markup=chat_keyboard
            )

            try:
                await message.bot.send_message(
                    match["id"],
                    "✅ مخاطب پیدا شد!\n\n"
                    "💬 می‌توانید شروع به چت کنید.",
                    reply_markup=chat_keyboard
                )
            except Exception as e:
                print(f"خطا در ارسال پیام به مخاطب: {e}")
        else:
            # Add to waiting list
            add_to_waiting(user_data)
            await message.answer(
                "⏳ در حال جستجوی مخاطب...\n\n"
                "لطفاً صبر کنید تا مخاطبی پیدا شود.",
                reply_markup=main_keyboard
            )

        await db.close()

    except Exception as e:
        print(f"خطا در فرآیند matching: {e}")
        await message.answer(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=main_keyboard
        )


# ==================== Special search ====================

@router.message(lambda m: m.text == "🎯 جستجوی ویژه")
async def special_search(message: Message):
    """جستجوی ویژه با فیلترهای بیشتر"""
    await message.answer(
        "🎯 <b>جستجوی ویژه</b>\n\n"
        "⚠️ این ویژگی به زودی فعال می‌شود!\n\n"
        "با این ویژگی می‌توانید:\n"
        "• جستجو بر اساس سن\n"
        "• جستجو بر اساس شهر\n"
        "• فیلترهای بیشتر",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )