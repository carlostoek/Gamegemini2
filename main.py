# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config.settings import settings
from database.db import init_db, get_db, insert_initial_data
from middlewares.db_middleware import DbSessionMiddleware
from middlewares.user_middleware import UserMiddleware
from scheduler.scheduler_config import setup_scheduler
from utils.logger import logger

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main() -> None:
    bot = Bot(settings.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()

    # Inicializar la base de datos y asegurar que los niveles, insignias y recompensas iniciales estén presentes
    await init_db()
    async for session in get_db():
        await insert_initial_data(session)
        break # Solo necesitamos una sesión para la inicialización

    # Middlewares
    dp.update.middleware(DbSessionMiddleware(session_pool=get_db))
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware()) # También para callbacks

    # Registrar routers
    from handlers.users import user_commands # Importación local
    from handlers.interactions import callback_handlers # Importación local
    from handlers.admin import admin_commands # Importación local
    from handlers.users import redeem_commands # Nueva importación

    dp.include_router(user_commands.router)
    dp.include_router(callback_handlers.router)
    dp.include_router(admin_commands.router)
    dp.include_router(redeem_commands.router) # Registrar el nuevo router

    # Configurar y arrancar el scheduler
    await setup_scheduler(bot)

    # Eliminar webhook y empezar a procesar actualizaciones
    logger.info("Bot iniciando polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    logger.info("Bot detenido.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente.")
    except Exception as e:
        logger.critical(f"Error fatal en el bot: {e}", exc_info=True)