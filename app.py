from aiogram import executor

from data.loader import scheduler
from utils.database import create_db


async def on_startup(dp):
    await create_db()
    scheduler.start()

if __name__ == '__main__':
    from handlers.menu_handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
