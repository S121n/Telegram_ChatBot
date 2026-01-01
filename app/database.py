import aiosqlite
from app.config import DATABASE_URL


# =========================
# اتصال به دیتابیس
# =========================
async def get_db():
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row
    return db


# =========================
# ساخت جداول دیتابیس
# =========================
async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.executescript("""
        -- =========================
        -- کاربران
        -- =========================
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            gender TEXT,
            province TEXT,
            city TEXT,
            age INTEGER,
            profile_pic TEXT,
            coins INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            banned_until TIMESTAMP
        );

        -- =========================
        -- سیستم دعوت
        -- =========================
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inviter_telegram_id INTEGER,
            invited_telegram_id INTEGER UNIQUE,
            referral_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- =========================
        -- ریپورت کاربران
        -- =========================
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER,
            reported_id INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- =========================
        -- پرداخت‌ها و سکه
        -- =========================
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            coins INTEGER,
            authority TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()