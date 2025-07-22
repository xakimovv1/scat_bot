# app.py
import asyncio
from aiogram import Bot, Dispatcher
from handlers.main import register_handlers  # <--- asosiy routerni ulaymiz

TOKEN = "7951148632:AAFMOB_CueliG5svW9M_PqaptkT8Fu9v8m4"  # <-- bu yerga o'z bot tokeningizni yozing

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Routerlarni ulash
register_handlers(dp)

async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
