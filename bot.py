from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers.start import router as start_router
from handlers.gamification import router as gamification_router
from handlers.leaderboard import router as leaderboard_router
from middlewares.auth import AuthMiddleware
from utils.logger import Logger

async def start_bot():
    logger = Logger.setup_logger()
    logger.info("Initializing bot...")
    
    bot = Bot(token=Config.get_bot_token())
    dp = Dispatcher(storage=MemoryStorage())
    
    # Registrar middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Registrar handlers
    dp.include_router(start_router)
    dp.include_router(gamification_router)
    dp.include_router(leaderboard_router)
    
    logger.info("Bot initialized successfully")
    return bot, dp

async def main():
    logger = Logger.setup_logger()
    bot, dp = await start_bot()
    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot session closed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
