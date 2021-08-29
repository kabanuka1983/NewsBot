from aiogram import Bot, types, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()
