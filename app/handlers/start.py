from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.database import get_db
from app.keyboards.main import main_keyboard
from app.handlers.register import RegisterState

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, state):
    db = await get_db()

    async with db.execute(
        "SELECT id FROM users WHERE telegram_id = ?",
        (message.from_user.id,)
    ) as cursor:
        user = await cursor.fetchone()

    if user:
        await message.answer("👋 خوش آمدید!", reply_markup=main_keyboard)
    else:
        await state.set_state(RegisterState.name)
        await message.answer("👤 نام خود را وارد کنید:")
