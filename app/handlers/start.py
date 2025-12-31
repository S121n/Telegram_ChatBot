from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.database import get_db
from app.keyboards.main import main_keyboard
from app.handlers.register import RegisterState

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    db = await get_db()

    # بررسی ثبت‌نام کاربر
    async with db.execute(
        "SELECT id FROM users WHERE telegram_id = ?",
        (message.from_user.id,)
    ) as cursor:
        user = await cursor.fetchone()

    # =========================
    # اگر کاربر قبلاً ثبت‌نام کرده
    # =========================
    if user:
        await message.answer(
            "👋 خوش آمدید!",
            reply_markup=main_keyboard
        )
        await db.close()
        return

    # =========================
    # اگر کاربر جدید است
    # =========================
    ref_id = None

    # پردازش لینک دعوت
    if message.text and "ref_" in message.text:
        try:
            ref_id = int(message.text.split("ref_")[1])
        except (IndexError, ValueError):
            ref_id = None

    # ذخیره ref_id در FSM
    if ref_id:
        await state.update_data(ref_id=ref_id)

    await state.set_state(RegisterState.name)

    await message.answer(
        "👤 نام خود را وارد کنید:"
    )

    await db.close()
