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

    # User registration check
    async with db.execute(
        "SELECT id FROM users WHERE telegram_id = ?",
        (message.from_user.id,)
    ) as cursor:
        user = await cursor.fetchone()

    # =========================
    # If the user has already registered
    # =========================
    if user:
        await message.answer(
            "👋 خوش آمدید!",
            reply_markup=main_keyboard
        )
        await db.close()
        return

    # =========================
    # If the user is new
    # =========================
    ref_id = None

    # Processing invitation link
    if message.text and "ref_" in message.text:
        try:
            ref_id = int(message.text.split("ref_")[1])
        except (IndexError, ValueError):
            ref_id = None

    # Store ref_id in FSM
    if ref_id:
        await state.update_data(ref_id=ref_id)

    await state.set_state(RegisterState.name)

    await message.answer(
        "👤 نام خود را وارد کنید:"
    )

    await db.close()
