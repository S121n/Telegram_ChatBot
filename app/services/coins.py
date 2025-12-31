from app.database import get_db


async def add_coins(telegram_id: int, coins: int):
    db = await get_db()
    await db.execute(
        "UPDATE users SET coins = coins + ? WHERE telegram_id = ?",
        (coins, telegram_id)
    )
    await db.commit()
    await db.close()


async def get_user_coins(telegram_id: int) -> int:
    db = await get_db()
    async with db.execute(
        "SELECT coins FROM users WHERE telegram_id = ?",
        (telegram_id,)
    ) as cursor:
        row = await cursor.fetchone()
    await db.close()
    return row[0] if row else 0
