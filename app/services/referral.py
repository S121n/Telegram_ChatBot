from app.database import get_db

REFERRAL_REWARD = 20

async def handle_referral(inviter_id: int, invited_id: int):
    if inviter_id == invited_id:
        return  # دعوت خود = ممنوع

    db = await get_db()

    # آیا قبلاً ثبت شده؟
    cursor = await db.execute(
        "SELECT id FROM referrals WHERE invited_id = ?",
        (invited_id,)
    )
    exists = await cursor.fetchone()

    if exists:
        await db.close()
        return

    # ثبت رفرال
    await db.execute(
        "INSERT INTO referrals (inviter_id, invited_id) VALUES (?, ?)",
        (inviter_id, invited_id)
    )

    # پاداش سکه
    await db.execute(
        "UPDATE users SET coins = coins + ? WHERE id = ?",
        (REFERRAL_REWARD, inviter_id)
    )

    await db.commit()
    await db.close()
