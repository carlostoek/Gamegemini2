import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties # <--- ¡Nueva importación!
from config.settings import settings
from database.db import init_db, get_db, insert_initial_data
from middlewares.db_middleware import DbSessionMiddleware
from middlewares.user_middleware import UserMiddleware
from scheduler.scheduler_config import setup_scheduler
from utils.logger import logger

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main() -> None:
    """
    Función principal que inicializa y arranca el bot de Telegram.
    """
    # ¡CAMBIO AQUÍ! Usar DefaultBotProperties para parse_mode
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    # Inicializar la base de datos y asegurar que los niveles, insignias y recompensas iniciales estén presentes
    await init_db()
    async for session in get_db():
        await insert_initial_data(session)
        break # Solo necesitamos una sesión para la inicialización

    # Middlewares: Se ejecutan antes de que los handlers procesen las actualizaciones.
    dp.update.middleware(DbSessionMiddleware(session_pool=get_db))
    # Pasamos las configuraciones (settings) al middleware de usuario
    dp.message.middleware(UserMiddleware(settings=settings)) # <--- ¡CAMBIO AQUÍ!
    dp.callback_query.middleware(UserMiddleware(settings=settings)) # <--- ¡CAMBIO AQUÍ!

    # Registrar routers: Agrupan los handlers de comandos y callbacks.
    # Importaciones locales para evitar problemas de dependencias circulares si los routers se importan en otros lugares.
    from handlers.users import user_commands
    from handlers.interactions import callback_handlers
    from handlers.admin import admin_commands
    from handlers.users import redeem_commands

    dp.include_router(user_commands.router)
    dp.include_router(callback_handlers.router)
    dp.include_router(admin_commands.router)
    dp.include_router(redeem_commands.router)

    # Configurar y arrancar el scheduler para tareas programadas (ej. puntos de permanencia)
    await setup_scheduler(bot)

    # Eliminar webhook existente (si lo hay) y empezar a procesar actualizaciones en modo polling
    logger.info("Bot iniciando polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    logger.info("Bot detenido.")

if __name__ == "__main__":
    # Punto de entrada principal para ejecutar el bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente por KeyboardInterrupt.")
    except Exception as e:
        logger.critical(f"Error fatal en el bot: {e}", exc_info=True)
