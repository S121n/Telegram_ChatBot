from aiogram import Router, F
from aiogram.types import Message

from app.database import get_db
from app.services.payments import create_payment
from app.keyboards.payments import coins_keyboard
from app.keyboards.main import main_keyboard

router = Router()

PACKAGES = {
    "💰 50 سکه - 25,000 تومان": (25000, 50),
    "💰 120 سکه - 50,000 تومان": (50000, 120),
    "💰 300 سکه - 100,000 تومان": (100000, 300),
}


# ================== Show coin purchase menu ==================
@router.message(F.text == "💳 خرید سکه")
async def show_coin_packages(message: Message):
    """نمایش پکیج‌های خرید سکه"""
    await message.answer(
        "💰 <b>خرید سکه</b>\n\n"
        "لطفاً یکی از پکیج‌های زیر را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=coins_keyboard
    )


# ================== Return to main menu ==================
@router.message(F.text == "🔙 بازگشت")
async def back_to_main_menu(message: Message):
    """بازگشت به منوی اصلی"""
    await message.answer(
        "🏠 منوی اصلی:",
        reply_markup=main_keyboard
    )


# ================== Start payment ==================
@router.message(F.text.in_(PACKAGES.keys()))
async def start_payment(message: Message):
    """شروع فرآیند پرداخت"""
    amount, coins = PACKAGES[message.text]

    authority, pay_url = await create_payment(
        amount=amount,
        description=f"خرید {coins} سکه"
    )

    if not authority:
        await message.answer(
            "❌ خطا در اتصال به درگاه پرداخت.\n"
            "لطفاً دوباره تلاش کنید.",
            reply_markup=coins_keyboard
        )
        return

    # Store payment information in the database
    try:
        db = await get_db()
        await db.execute(
            """
            INSERT INTO payments (user_id, amount, coins, authority)
            VALUES (?, ?, ?, ?)
            """,
            (message.from_user.id, amount, coins, authority)
        )
        await db.commit()
        await db.close()

        await message.answer(
            f"💳 <b>اطلاعات پرداخت:</b>\n\n"
            f"💰 مبلغ: {amount:,} تومان\n"
            f"🎁 دریافت: {coins} سکه\n\n"
            f"🔗 برای پرداخت روی لینک زیر کلیک کنید:\n"
            f"{pay_url}\n\n"
            f"⚠️ پس از پرداخت، سکه‌ها به حساب شما اضافه می‌شود.",
            parse_mode="HTML",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در ذخیره اطلاعات پرداخت: {e}")
        await message.answer(
            "❌ خطا در ثبت اطلاعات پرداخت.",
            reply_markup=coins_keyboard
        )