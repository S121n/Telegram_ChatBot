from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.database import get_db
from app.keyboards.main import main_keyboard
from app.keyboards.province import province_keyboard
from app.keyboards.city import city_keyboard
from app.utils.iran_locations import IRAN_PROVINCES

router = Router()


# =======================
# FSM States
# =======================
class RegisterState(StatesGroup):
    name = State()
    gender = State()
    province = State()
    city = State()
    age = State()
    photo = State()


# =======================
# STEP 1: NAME
# =======================
@router.message(RegisterState.name)
async def register_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ نام معتبر وارد کنید.")
        return

    await state.update_data(name=name)
    await state.set_state(RegisterState.gender)

    gender_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="پسر"), KeyboardButton(text="دختر")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🚻 جنسیت خود را انتخاب کنید:",
        reply_markup=gender_keyboard
    )


# =======================
# STEP 2: GENDER
# =======================
@router.message(RegisterState.gender)
async def register_gender(message: Message, state: FSMContext):
    if message.text not in ["پسر", "دختر"]:
        await message.answer("❌ فقط از دکمه‌ها استفاده کنید.")
        return

    await state.update_data(gender=message.text)
    await state.set_state(RegisterState.province)

    await message.answer(
        "📍 استان خود را انتخاب کنید:",
        reply_markup=province_keyboard()
    )


# =======================
# STEP 3: PROVINCE
# =======================
@router.message(RegisterState.province)
async def register_province(message: Message, state: FSMContext):
    province = message.text

    if province not in IRAN_PROVINCES:
        await message.answer(
            "❌ استان را فقط از کیبورد انتخاب کنید.",
            reply_markup=province_keyboard()
        )
        return

    await state.update_data(province=province)
    await state.set_state(RegisterState.city)

    await message.answer(
        "🏙️ شهر خود را انتخاب کنید:",
        reply_markup=city_keyboard(province)
    )


# =======================
# STEP 4: CITY
# =======================
@router.message(RegisterState.city)
async def register_city(message: Message, state: FSMContext):
    city = message.text
    data = await state.get_data()
    province = data.get("province")

    if city not in IRAN_PROVINCES.get(province, []):
        await message.answer(
            "❌ شهر را فقط از کیبورد انتخاب کنید.",
            reply_markup=city_keyboard(province)
        )
        return

    await state.update_data(city=city)
    await state.set_state(RegisterState.age)

    await message.answer(
        "🎂 سن خود را وارد کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="18"), KeyboardButton(text="20"), KeyboardButton(text="25")]],
            resize_keyboard=True
        )
    )


# =======================
# STEP 5: AGE
# =======================
@router.message(RegisterState.age)
async def register_age(message: Message, state: FSMContext):
    text = message.text.strip()

    # بررسی عدد بودن
    if not text.isdigit():
        await message.answer("❌ لطفاً سن خود را فقط به صورت عدد وارد کنید.")
        return

    age = int(text)

    # شرط سنی
    if age <= 14:
        await message.answer("❌ سن شما باید بالای ۱۴ سال باشد.")
        return

    if age > 100:
        await message.answer("❌ لطفاً سن معتبر وارد کنید.")
        return

    await state.update_data(age=age)
    await state.set_state(RegisterState.photo)

    await message.answer(
        "🖼️ لطفاً یک عکس پروفایل ارسال کنید:",
        reply_markup=None
    )


# =======================
# STEP 6: PHOTO + SAVE USER
# =======================
@router.message(RegisterState.photo)
async def register_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ لطفاً فقط عکس ارسال کنید.")
        return

    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    db = await get_db()

    await db.execute(
        """
        INSERT INTO users 
        (telegram_id, name, gender, province, city, age, profile_pic, coins)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message.from_user.id,
            data["name"],
            data["gender"],
            data["province"],
            data["city"],
            data["age"],
            photo_id,
            15  # 🎁 سکه اولیه
        )
    )

    await db.commit()
    await db.close()

    await state.clear()

    await message.answer(
        "✅ ثبت‌نام شما با موفقیت انجام شد!\n\n"
        "🎁 ۱۵ سکه به حساب شما اضافه شد.",
        reply_markup=main_keyboard
    )
