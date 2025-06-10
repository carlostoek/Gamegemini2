# scheduler/scheduler_config.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from utils.logger import logger
from .jobs import award_permanence_points_job
from aiogram import Bot

scheduler = AsyncIOScheduler()

async def setup_scheduler(bot: Bot):
    """
    Configura y arranca el scheduler para las tareas programadas.
    """
    logger.info("Configurando scheduler...")

    # Calcula la próxima ejecución para que ocurra en un horario específico si se desea
    # Por ejemplo, cada día a las 00:01 AM (hora del servidor)
    # next_run_time_daily = datetime.now()
    # if next_run_time_daily.hour >= 0 and next_run_time_daily.minute >= 1:
    #     next_run_time_daily += timedelta(days=1)
    # next_run_time_daily = next_run_time_daily.replace(hour=0, minute=1, second=0, microsecond=0)

    # Cada 24 horas para el chequeo de permanencia.
    # Podríamos hacerlo semanalmente para reducir la carga de la DB si los usuarios son muchos,
    # pero el informe pide puntos semanales con racha, así que un chequeo diario es mejor.
    scheduler.add_job(
        award_permanence_points_job,
        trigger=IntervalTrigger(hours=24), # Se ejecuta cada 24 horas
        # next_run_time=next_run_time_daily, # Descomentar para una hora específica
        args=[bot], # Pasar el objeto bot al job
        id='award_permanence_points',
        name='Otorgar puntos por permanencia'
    )
    logger.info("Job 'award_permanence_points' añadido al scheduler (cada 24h).")

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler iniciado.")
    else:
        logger.info("Scheduler ya está corriendo.")