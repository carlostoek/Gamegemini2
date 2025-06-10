# el_juego_del_divan/database/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from sqlalchemy.future import select
import asyncio

# === CAMBIO APLICADO: Importaciones corregidas sin el prefijo 'el_juego_del_divan' ===
from config.settings import settings
from utils.logger import logger
from database.base_model import Base # Esta importación es correcta tal cual está

# Asegúrate de que todos tus modelos sean importados aquí
from database.models.user import User
from database.models.level import Level, INITIAL_LEVELS
from database.models.badge import Badge, INITIAL_BADGES
from database.models.purchase import Purchase
from database.models.reward import Reward, INITIAL_REWARDS
from database.models.mission import Mission
# ======================================================================================

DATABASE_URL = settings.DATABASE_URL

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async def init_db():
    logger.info("Inicializando la base de datos...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos inicializada correctamente.")

async def insert_initial_data(session: AsyncSession):
    """Inserta los niveles, insignias y recompensas iniciales si las tablas están vacías."""
    result_levels = await session.execute(select(Level))
    if not result_levels.scalars().first():
        logger.info("No se encontraron niveles, insertando niveles iniciales...")
        for level_data in INITIAL_LEVELS:
    
            session.add(Level(**level_data))
        await session.commit()
        logger.info("Niveles iniciales insertados correctamente.")
    else:
        logger.info("Los niveles ya existen en la base de datos.")

    result_badges = await session.execute(select(Badge))
    if not result_badges.scalars().first():
        logger.info("No se encontraron insignias, insertando insignias iniciales...")
        for badge_data in INITIAL_BADGES:
            session.add(Badge(**badge_data))
        await session.commit()
        logger.info("Insignias iniciales insertadas correctamente.")
    else:
        logger.info("Las insignias ya existen en la base de datos.")

    result_rewards = await session.execute(select(Reward))
    if not result_rewards.scalars().first():
        logger.info("No se encontraron recompensas, insertando recompensas iniciales...")
        for reward_data in INITIAL_REWARDS:
            session.add(Reward(**reward_data))
        await session.commit()
        logger.info("Recompensas iniciales insertadas correctamente.")
    else:
        logger.info("Las recompensas ya existen en la base de datos.")

@asynccontextmanager
async def get_db():
    async with async_session_maker() as session:
        yield session

# if __name__ == "__main__":
#     async def _run_init_and_seed():
#         await init_db()
#         async with async_session_maker() as session:
#             await insert_initial_data(session)
#     logger.info("Ejecutando script de inicialización de DB (db.py).")
#     try:
#         asyncio.run(_run_init_and_seed())
#     except Exception as e:
#         logger.critical(f"Error fatal durante la inicialización de la DB: {e}", exc_info=True)
#     logger.info("Script de inicialización de DB finalizado.")
