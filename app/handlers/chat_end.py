from aiogram import Router
from aiogram.types import Message

from app.services.matcher import end_chat
from app.keyboards.main import main_keyboard

router = Router()


@router.message(lambda m: m.text == "❌ اتمام چت")
async def end_chat_handler(message: Message):
    partner_id = end_chat(message.from_user.id)

    await message.answer("❌ چت پایان یافت.", reply_markup=main_keyboard)

    if partner_id:
        await message.bot.send_message(
            partner_id,
            "❌ مخاطب چت را ترک کرد.",
            reply_markup=main_keyboard
        )
