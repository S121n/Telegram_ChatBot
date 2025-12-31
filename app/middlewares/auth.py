from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.database import get_db


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):

        if not isinstance(event, Message):
            return await handler(event, data)

        state: FSMContext | None = data.get("state")


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

        if not user and event.text != "/start":
            await event.answer("❌ ابتدا باید ثبت‌نام کنید.")
            return

        return await handler(event, data)
