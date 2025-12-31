from datetime import datetime
from aiogram.types import Message, CallbackQuery

from app.database import get_db


class BanMiddleware:
    async def __call__(self, handler, event, data):

        user = None

        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if not user:
            return await handler(event, data)

        db = await get_db()

        async with db.execute(
            "SELECT banned_until FROM users WHERE telegram_id = ?",
            (user.id,)
        ) as cursor:
            row = await cursor.fetchone()

        await db.close()

        # If the user is not registered
        if not row:
            return await handler(event, data)

        banned_until = row["banned_until"]

        # If not banned
        if not banned_until:
            return await handler(event, data)

        # Date conversion
        try:
            banned_until_dt = datetime.fromisoformat(banned_until)
        except Exception:
            # If the date is broken, let it go
            return await handler(event, data)

        # Check the end of the bin
        if banned_until_dt <= datetime.now():
            return await handler(event, data)

        # The user is Ben
        remaining = banned_until_dt - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600

        await event.answer(
            f"⛔ حساب شما مسدود شده است.\n\n"
            f"⏳ زمان باقی‌مانده:\n"
            f"{days} روز و {hours} ساعت",
            show_alert=True if isinstance(event, CallbackQuery) else False
        )

        return
