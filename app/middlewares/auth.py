from aiogram import BaseMiddleware
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.database import get_db


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):

        if not isinstance(event, Message):
            return await handler(event, data)

        state: FSMContext | None = data.get("state")

        # اگر کاربر داخل FSM است، مزاحم نشو
        if state:
            current_state = await state.get_state()
            if current_state is not None:
                return await handler(event, data)

        db = await get_db()
        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (event.from_user.id,)
        ) as cursor:
            user = await cursor.fetchone()
        await db.close()

        # اگر ثبت‌نام نکرده
        if not user:
            # اجازه بده /start یا "ثبت نام" عبور کند
            if event.text in ("/start", "ثبت نام"):
                return await handler(event, data)

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="ثبت نام")]
                ],
                resize_keyboard=True
            )

            await event.answer(
                "👋 خوش آمدید\nبرای استفاده از ربات ابتدا باید ثبت‌نام کنید.",
                reply_markup=keyboard
            )
            return

        return await handler(event, data)
