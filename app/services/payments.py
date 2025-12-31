import aiohttp
from app.config import (
    ZARINPAL_MERCHANT_ID,
    ZARINPAL_REQUEST_URL,
    ZARINPAL_VERIFY_URL,
    CALLBACK_URL
)


async def create_payment(amount: int, description: str):
    data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "description": description,
        "callback_url": CALLBACK_URL
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ZARINPAL_REQUEST_URL, json=data) as resp:
            result = await resp.json()

    if result.get("data") and result["data"]["code"] == 100:
        authority = result["data"]["authority"]
        pay_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
        return authority, pay_url

    return None, None


async def verify_payment(authority: str, amount: int):
    data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "authority": authority,
        "amount": amount
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ZARINPAL_VERIFY_URL, json=data) as resp:
            result = await resp.json()

    if result.get("data") and result["data"]["code"] == 100:
        return True

    return False
