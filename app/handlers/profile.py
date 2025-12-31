from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

from app.database import get_db
from app.keyboards.profile import profile_kb
from app.keyboards.main import main_keyboard
from app.keyboards.province import province_keyboard
from app.keyboards.city import city_keyboard
from app.utils.iran_locations import IRAN_PROVINCES
from app.config import BOT_USERNAME


router = Router()


# FSM States for profile editing
class EditProfileState(StatesGroup):
    name = State()
    province = State()
    city = State()
    age = State()
    photo = State()


@router.message(F.text == "👤 پروفایل من")
async def show_my_profile(message: Message):
    """نمایش پروفایل کاربر"""
    user_id = message.from_user.id

    try:
        db = await get_db()
        db.row_factory = aiosqlite.Row

        async with db.execute(
                """
                SELECT name, gender, age, province, city, profile_pic, coins
                FROM users
                WHERE telegram_id = ?
                """,
                (user_id,)
        ) as cursor:
            row = await cursor.fetchone()

        await db.close()

        if not row:
            await message.answer(
                "❌ پروفایل شما یافت نشد.\n"
                "لطفاً دوباره ثبت‌نام کنید: /start"
            )
            return

        user = dict(row)

        gender_fa = "پسر" if user['gender'] == "پسر" else "دختر"

        text = (
            f"👤 <b>پروفایل من</b>\n\n"
            f"🔹 نام: {user['name']}\n"
            f"🔹 جنسیت: {gender_fa}\n"
            f"🔹 سن: {user['age']} سال\n"
            f"📍 {user['province']} - {user['city']}\n"
            f"💰 سکه: {user['coins']}"
        )

        if user.get('profile_pic'):
            await message.answer_photo(
                photo=user['profile_pic'],
                caption=text,
                parse_mode="HTML",
                reply_markup=profile_kb()
            )
        else:
            await message.answer(
                text,
                parse_mode="HTML",
                reply_markup=profile_kb()
            )

    except Exception as e:
        print(f"خطا در نمایش پروفایل: {e}")
        await message.answer("❌ خطا در دریافت اطلاعات پروفایل.")


# ==================== Callback Handlers ====================

@router.callback_query(F.data == "edit_name")
async def edit_name_callback(callback: CallbackQuery, state: FSMContext):
    """شروع ویرایش نام"""
    await state.set_state(EditProfileState.name)
    await callback.message.answer("✏️ نام جدید خود را وارد کنید:")
    await callback.answer()


@router.callback_query(F.data == "edit_province")
async def edit_province_callback(callback: CallbackQuery, state: FSMContext):
    """شروع ویرایش استان"""
    await state.set_state(EditProfileState.province)
    await callback.message.answer(
        "📍 استان جدید خود را انتخاب کنید:",
        reply_markup=province_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "edit_city")
async def edit_city_callback(callback: CallbackQuery, state: FSMContext):
    """شروع ویرایش شهر"""
    user_id = callback.from_user.id

    try:
        db = await get_db()
        async with db.execute(
                "SELECT province FROM users WHERE telegram_id = ?",
                (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
        await db.close()

        if result:
            province = result[0]
            await state.update_data(province=province)
            await state.set_state(EditProfileState.city)
            await callback.message.answer(
                "🏙️ شهر جدید خود را انتخاب کنید:",
                reply_markup=city_keyboard(province)
            )
        else:
            await callback.message.answer("❌ ابتدا استان خود را تنظیم کنید.")
    except Exception as e:
        print(f"خطا در edit_city: {e}")
        await callback.message.answer("❌ خطایی رخ داد.")

    await callback.answer()


@router.callback_query(F.data == "edit_age")
async def edit_age_callback(callback: CallbackQuery, state: FSMContext):
    """شروع ویرایش سن"""
    await state.set_state(EditProfileState.age)
    await callback.message.answer("🎂 سن جدید خود را وارد کنید (عدد):")
    await callback.answer()


@router.callback_query(F.data == "edit_photo")
async def edit_photo_callback(callback: CallbackQuery, state: FSMContext):
    """شروع ویرایش عکس پروفایل"""
    await state.set_state(EditProfileState.photo)
    await callback.message.answer("🖼️ عکس پروفایل جدید خود را ارسال کنید:")
    await callback.answer()


# ==================== FSM Handlers for Editing ====================

@router.message(EditProfileState.name)
async def update_name(message: Message, state: FSMContext):
    """ذخیره نام جدید"""
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ نام معتبر وارد کنید.")
        return

    try:
        db = await get_db()
        await db.execute(
            "UPDATE users SET name = ? WHERE telegram_id = ?",
            (name, message.from_user.id)
        )
        await db.commit()
        await db.close()

        await state.clear()
        await message.answer(
            f"✅ نام شما به '{name}' تغییر یافت.",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در update_name: {e}")
        await message.answer("❌ خطا در بروزرسانی نام.")


@router.message(EditProfileState.province)
async def update_province(message: Message, state: FSMContext):
    """ذخیره استان جدید"""
    province = message.text

    if province not in IRAN_PROVINCES:
        await message.answer(
            "❌ لطفاً استان را از کیبورد انتخاب کنید.",
            reply_markup=province_keyboard()
        )
        return

    await state.update_data(province=province)
    await state.set_state(EditProfileState.city)
    await message.answer(
        "🏙️ شهر خود را انتخاب کنید:",
        reply_markup=city_keyboard(province)
    )


@router.message(EditProfileState.city)
async def update_city(message: Message, state: FSMContext):
    """ذخیره شهر جدید"""
    city = message.text
    data = await state.get_data()
    province = data.get("province")

    if city not in IRAN_PROVINCES.get(province, []):
        await message.answer(
            "❌ لطفاً شهر را از کیبورد انتخاب کنید.",
            reply_markup=city_keyboard(province)
        )
        return

    try:
        db = await get_db()
        await db.execute(
            "UPDATE users SET province = ?, city = ? WHERE telegram_id = ?",
            (province, city, message.from_user.id)
        )
        await db.commit()
        await db.close()

        await state.clear()
        await message.answer(
            f"✅ موقعیت شما به '{province} - {city}' تغییر یافت.",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در update_city: {e}")
        await message.answer("❌ خطا در بروزرسانی موقعیت.")


@router.message(EditProfileState.age)
async def update_age(message: Message, state: FSMContext):
    """ذخیره سن جدید"""
    text = message.text.strip()

    if not text.isdigit():
        await message.answer("❌ لطفاً فقط عدد وارد کنید.")
        return

    age = int(text)

    if age <= 14 or age > 100:
        await message.answer("❌ سن باید بین 15 تا 100 باشد.")
        return

    try:
        db = await get_db()
        await db.execute(
            "UPDATE users SET age = ? WHERE telegram_id = ?",
            (age, message.from_user.id)
        )
        await db.commit()
        await db.close()

        await state.clear()
        await message.answer(
            f"✅ سن شما به {age} تغییر یافت.",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در update_age: {e}")
        await message.answer("❌ خطا در بروزرسانی سن.")


@router.message(EditProfileState.photo)
async def update_photo(message: Message, state: FSMContext):
    """ذخیره عکس پروفایل جدید"""
    if not message.photo:
        await message.answer("❌ لطفاً فقط عکس ارسال کنید.")
        return

    photo_id = message.photo[-1].file_id

    try:
        db = await get_db()
        await db.execute(
            "UPDATE users SET profile_pic = ? WHERE telegram_id = ?",
            (photo_id, message.from_user.id)
        )
        await db.commit()
        await db.close()

        await state.clear()
        await message.answer(
            "✅ عکس پروفایل شما تغییر یافت.",
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"خطا در update_photo: {e}")
        await message.answer("❌ خطا در بروزرسانی عکس.")


@router.message(F.text == "🎁 دعوت دوستان")
async def invite_friends(message: Message):
    db = await get_db()

    async with db.execute(
        "SELECT id FROM users WHERE telegram_id = ?",
        (message.from_user.id,)
    ) as cursor:
        user = await cursor.fetchone()

    await db.close()

    if not user:
        await message.answer("❌ ابتدا باید ثبت‌نام کنید.")
        return

    user_id = user["id"]

    invite_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    await message.answer(
        "🤝 <b>لینک دعوت اختصاصی شما:</b>\n\n"
        f"{invite_link}\n\n"
        "🎁 با هر ثبت‌نام موفق از طریق این لینک، ۱۵ سکه هدیه می‌گیرید!",
        parse_mode="HTML"
    )
