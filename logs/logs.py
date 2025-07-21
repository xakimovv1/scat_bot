@router.message(F.text == "/logs")
async def show_logs(msg: Message):
    if msg.from_user.id not in active_admins:
        await msg.answer("❌ Siz admin sifatida tizimga kirmagansiz. Avval /admin buyrug‘ini yuboring.")
        return

    try:
        with open("logs/payments.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-10:]
        if lines:
            await msg.answer("🧾 Oxirgi to‘lovlar:\n\n" + "".join(lines))
        else:
            await msg.answer("📁 Hozircha hech qanday to‘lov yozuvi yo‘q.")
    except FileNotFoundError:
        await msg.answer("📂 Log fayli topilmadi.")
