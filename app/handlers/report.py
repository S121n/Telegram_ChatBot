from aiogram import Router, F
from aiogram.types import Message

from app.database import get_db
from app.services.matcher import active_chats  # ✅ اصلاح شده

router = Router()


@router.message(F.text == "🚫 ریپورت")
async def report_user(message: Message):
    """ریپورت کردن مخاطب فعلی"""
    reporter_id = message.from_user.id
    reported_id = active_chats.get(reporter_id)

    if not reported_id:
        await message.answer("❌ کاربری برای ریپورت وجود ندارد.")
        return

    try:
        db = await get_db()

        await db.execute(
            """
            INSERT INTO reports (reporter_id, reported_id)
            VALUES (?, ?)
            """,
            (reporter_id, reported_id)
        )

        await db.commit()
        await db.close()

        await message.answer("✅ گزارش شما ثبت شد و بررسی خواهد شد.")

    except Exception as e:
        print(f"خطا در ثبت ریپورت: {e}")
        await message.answer("❌ خطا در ثبت گزارش.")