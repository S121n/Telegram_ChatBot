from datetime import datetime
from aiogram.types import Message, CallbackQuery

from app.database import get_db


class BanMiddleware:
    async def __call__(self, handler, event, data):
        # رویدادهایی که کاربر ندارند (مثلاً service message)
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

        # اگر کاربر ثبت‌نام نکرده باشد
        if not row:
            return await handler(event, data)

        banned_until = row["banned_until"]

        # اگر بن نشده
        if not banned_until:
            return await handler(event, data)

        # تبدیل تاریخ
        try:
            banned_until_dt = datetime.fromisoformat(banned_until)
        except Exception:
            # اگر تاریخ خراب باشد، اجازه بده
            return await handler(event, data)

        # بررسی پایان بن
        if banned_until_dt <= datetime.now():
            return await handler(event, data)

        # کاربر بن است
        remaining = banned_until_dt - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600

        await event.answer(
            f"⛔ حساب شما مسدود شده است.\n\n"
            f"⏳ زمان باقی‌مانده:\n"
            f"{days} روز و {hours} ساعت",
            show_alert=True if isinstance(event, CallbackQuery) else False
        )

        return  # ❌ ادامه پردازش متوقف می‌شود
