# scheduler/jobs.py
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from services.permanence_service import PermanenceService
from utils.logger import logger
from aiogram import Bot

async def award_permanence_points_job(bot: Bot):
    """
    Tarea programada para otorgar puntos de permanencia a los usuarios.
    Se ejecuta periódicamente (e.g., una vez al día o cada semana).
    """
    logger.info("Iniciando job de otorgamiento de puntos por permanencia...")
    try:
        async for session in get_db():
            permanence_service = PermanenceService(session, bot)
            awarded_count = await permanence_service.award_weekly_permanence_points()
            logger.info(f"Finalizado job de permanencia. Puntos otorgados a {awarded_count} usuarios.")
            # Si hay lógica mensual separada, se llamaría aquí también
            # await permanence_service.award_monthly_permanence_points()
    except Exception as e:
        logger.error(f"Error en el job de permanencia: {e}", exc_info=True)

# Puedes añadir más jobs aquí si son necesarios
# Por ejemplo, para reseteo diario de misiones, sorteos mensuales, etc.