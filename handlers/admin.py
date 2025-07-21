# handlers/admin.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
import os, json

from config import ADMINS
from utils.balans import apply_fine, approve_payment

router = Router()

@router.message(F.text == "/adminpanel")
async def admin_panel(msg: Message):
    if msg.from_user.id not in ADMINS:
        await msg.answer("⛔ Siz admin emassiz.")
        return

    try:
        files = os.listdir("pending")
        if not files:
            await msg.answer("🗂 Hozircha tasdiqlanmagan to‘lovlar yo‘q.")
            return
    except:
        await msg.answer("📂 Fayllar katalogi topilmadi.")
        return

    for filename in files:
        with open(f"pending/{filename}", "r", encoding="utf-8") as f:
            data = json.load(f)

        photo_path = data["photo_path"]
        caption = (
            f"📌 Pozivnoy: {data['pozivnoy']}\n"
            f"💰 Kiritilgan summa: {data['entered_sum']} so'm\n"
            f"🧾 OCR topgan summa: {data['detected_sum']} so'm\n"
            f"📅 Sana: {data['date']}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm:{filename}"),
                InlineKeyboardButton(text="❌ Ko‘p pul olgan", callback_data=f"fine:{filename}")
            ]
        ])

        photo = FSInputFile(photo_path)
        await msg.answer_photo(photo=photo, caption=caption, reply_markup=keyboard)

@router.callback_query(F.data.startswith("confirm:"))
async def confirm_payment(call: CallbackQuery):
    file = call.data.split(":")[1]
    with open(f"pending/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)

    approve_payment(data["pozivnoy"], int(data["entered_sum"]))
    os.remove(f"pending/{file}")
    await call.message.edit_caption(call.message.caption + "\n\n✅ Tasdiqlandi.")
    await call.answer("Tasdiqlandi!")

@router.callback_query(F.data.startswith("fine:"))
async def fine_payment(call: CallbackQuery):
    file = call.data.split(":")[1]
    with open(f"pending/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)

    apply_fine(data["pozivnoy"], int(data["entered_sum"]), int(data["detected_sum"]))
    os.remove(f"pending/{file}")
    await call.message.edit_caption(call.message.caption + "\n\n❌ Jarima qo‘llandi.")
    await call.answer("Jarima qo‘llandi.")
