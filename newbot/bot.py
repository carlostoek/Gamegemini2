import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from .config import config
from .handlers.commands import router
from .models import Base
from .database import engine
from .utils.logger import logger

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB ready")

async def main():
    bot = Bot(config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await on_startup()
    await bot.set_my_commands([BotCommand(command="start", description="Inicio"), BotCommand(command="leaderboard", description="Ranking")])
    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
