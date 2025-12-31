from fastapi import FastAPI, Request
from app.database import get_db
from app.services.payments import verify_payment
from app.services.coins import add_coins

app = FastAPI()


@app.get("/payment/callback")
async def payment_callback(request: Request):
    authority = request.query_params.get("Authority")
    status = request.query_params.get("Status")

    if status != "OK":
        return {"message": "پرداخت ناموفق بود"}

    db = await get_db()
    async with db.execute(
        "SELECT * FROM payments WHERE authority = ? AND status = 'pending'",
        (authority,)
    ) as cursor:
        payment = await cursor.fetchone()

    if not payment:
        await db.close()
        return {"message": "پرداخت قبلاً بررسی شده"}

    success = await verify_payment(authority, payment["amount"])

    if not success:
        await db.execute(
            "UPDATE payments SET status = 'failed' WHERE authority = ?",
            (authority,)
        )
        await db.commit()
        await db.close()
        return {"message": "پرداخت تایید نشد"}

    # موفق
    await db.execute(
        "UPDATE payments SET status = 'success' WHERE authority = ?",
        (authority,)
    )
    await db.commit()
    await db.close()

    await add_coins(payment["user_id"], payment["coins"])

    return {"message": "پرداخت با موفقیت انجام شد"}
