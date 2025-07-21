from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os, datetime
from config import ADMINS
from utils.scat_api import check_pay, do_pay

router = Router()
active_admins = set()

# Guruhga yuborish uchun username (bot admin bo‘lishi kerak)
GROUP_USERNAME = "@xizmattekshiruvbot1"

class PayStates(StatesGroup):
    pozivnoy = State()
    summa = State()
    screenshot = State()
    admin_login = State()
    admin_password = State()

@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await msg.answer("🚖 Pozivnoy raqamingizni kiriting:")
    await state.set_state(PayStates.pozivnoy)

@router.message(PayStates.pozivnoy)
async def get_pozivnoy(msg: Message, state: FSMContext):
    await state.update_data(pozivnoy=msg.text.strip().upper())
    await msg.answer("💰 To‘lov summasini kiriting:")
    await state.set_state(PayStates.summa)

@router.message(PayStates.summa)
async def get_summa(msg: Message, state: FSMContext):
    await state.update_data(summa=msg.text.strip())
    await msg.answer("📷 Endi skrinshotni yuboring:")
    await state.set_state(PayStates.screenshot)

@router.message(PayStates.screenshot, F.photo)
async def get_screenshot(msg: Message, state: FSMContext):
    data = await state.get_data()
    pozivnoy = data["pozivnoy"]
    entered_summa = data["summa"]

    photo = msg.photo[-1]
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{msg.from_user.id}_{photo.file_id}.jpg"

    bot: Bot = msg.bot
    file = await bot.get_file(photo.file_id)
    await bot.download_file(file.file_path, destination=path)

    await msg.answer("✅ Chekingiz qabul qilindi. Adminlar tomonidan ko‘rib chiqiladi.")

    # OCR yo‘q, shunchaki dummy qiymatlar
    detected_summa = "NOMA'LUM"
    karta = "0000"
    txn_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    code, check_resp = check_pay(pozivnoy, txn_id, entered_summa)

    success = False
    if code == 200 and "<result>0</result>" in check_resp:
        code2, pay_resp = do_pay(pozivnoy, txn_id, entered_summa)
        if code2 == 200 and "<result>0</result>" in pay_resp:
            await msg.answer("✅ To‘lov tasdiqlandi va balansga tushirildi!")
            success = True
        else:
            await msg.answer("❌ To‘lov amalga oshmadi:\n" + pay_resp)
    else:
        await msg.answer("❌ Tekshiruvda xatolik:\n" + check_resp)

    await log_payment(bot, msg.from_user.id, pozivnoy, entered_summa, detected_summa, karta, txn_id, path, success, photo)
    await state.clear()

async def log_payment(bot: Bot, user_id, pozivnoy, entered_summa, detected_summa, card, txn_id, screenshot_path, success, photo):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    vaqt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ MUVAFFAQIYATLI" if success else "❌ XATO"

    log_msg = (
        f"{vaqt}\n"
        f"🆔 TXN ID: {txn_id}\n"
        f"👤 User ID: {user_id}\n"
        f"📌 Pozivnoy: {pozivnoy}\n"
        f"💰 Kiritilgan summa: {entered_summa} so'm\n"
        f"🔍 Chekdagi summa: {detected_summa} so'm\n"
        f"💳 Karta: {card}\n"
        f"📥 Status: {status}\n"
        f"-----------------------------"
    )

    with open(os.path.join(log_dir, "payments.log"), "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

    # Guruhga skrinshot va logni yuborish
    await bot.send_photo(
        chat_id=GROUP_USERNAME,
        photo=photo.file_id,
        caption=log_msg
    )

@router.message(F.text == "/admin")
async def admin_start(msg: Message, state: FSMContext):
    await msg.answer("🛡 Admin loginini kiriting:")
    await state.set_state(PayStates.admin_login)

@router.message(PayStates.admin_login)
async def get_admin_login(msg: Message, state: FSMContext):
    await state.update_data(admin_login=msg.text.strip())
    await msg.answer("🛡 Parolni kiriting:")
    await state.set_state(PayStates.admin_password)

@router.message(PayStates.admin_password)
async def get_admin_password(msg: Message, state: FSMContext):
    data = await state.get_data()
    if data["admin_login"] == "admin" and msg.text.strip() == "admin":
        active_admins.add(msg.from_user.id)
        await msg.answer("✅ Admin panelga xush kelibsiz!\n/logs buyrug‘i orqali to‘lovlar ro‘yxatini ko‘ring.")
    else:
        await msg.answer("❌ Login yoki parol xato!")
    await state.clear()

@router.message(F.text == "/logs")
async def show_logs(msg: Message):
    if msg.from_user.id not in active_admins:
        await msg.answer("❌ Siz admin emassiz. Avval /admin buyrug‘ini kiriting.")
        return

    try:
        with open("logs/payments.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-10:]
        if lines:
            await msg.answer("🧾 Oxirgi to‘lovlar:\n\n" + "".join(lines))
        else:
            await msg.answer("📂 Hali hech qanday yozuv mavjud emas.")
    except FileNotFoundError:
        await msg.answer("📂 Log fayli topilmadi.")

def register_handlers(dp):
    dp.include_router(router)
