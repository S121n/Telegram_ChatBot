import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN
from app.database import init_db

# Routers
from app.handlers.start import router as start_router
from app.handlers.register import router as register_router
from app.handlers.profile import router as profile_router
from app.handlers.match import router as match_router
from app.handlers.report import router as report_router
from app.handlers.chat import router as chat_router
from app.handlers.payments import router as payments_router

# Middlewares
from app.middlewares.auth import AuthMiddleware
from app.middlewares.ban import BanMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Middlewares (ترتیب مهم است)
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Routers (ترتیب حیاتی است - از خاص به عام)
    dp.include_router(start_router)       # 1️⃣ /start
    dp.include_router(register_router)    # 2️⃣ ثبت‌نام
    dp.include_router(profile_router)     # 3️⃣ پروفایل + دعوت دوستان
    dp.include_router(payments_router)    # 4️⃣ خرید سکه (باید قبل از match باشد)
    dp.include_router(match_router)       # 5️⃣ جستجوی مخاطب
    dp.include_router(report_router)      # 6️⃣ ریپورت
    dp.include_router(chat_router)        # 7️⃣ چت (باید آخرین باشد)

    # ایجاد جداول دیتابیس
    await init_db()

    print("✅ ربات با موفقیت راه‌اندازی شد!")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())