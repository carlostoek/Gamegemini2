# database/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy.future import select

# Importar Base desde su nuevo archivo separado
from database.base_model import Base # <--- CAMBIO IMPORTANTE

from config.settings import settings
from utils.logger import logger

# Importar modelos para que Base.metadata.create_all los reconozca
# ¡IMPORTANTE! Aquí SÍ deben estar todos tus modelos para que las tablas se creen
from database.models.user import User
from database.models.level import Level, INITIAL_LEVELS
from database.models.badge import Badge, INITIAL_BADGES
from database.models.purchase import Purchase
from database.models.reward import Reward, INITIAL_REWARDS

DATABASE_URL = settings.DATABASE_URL

# Base ya no se define aquí, se importa
engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """
    Inicializa la base de datos: crea todas las tablas definidas en Base.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos inicializada correctamente.")

async def insert_initial_data(session: AsyncSession):
    """Inserta los niveles, insignias y recompensas iniciales si las tablas están vacías."""
    # Insertar niveles
    result_levels = await session.execute(select(Level))
    if not result_levels.scalars().first():
        logger.info("No se encontraron niveles, insertando niveles iniciales...")
        for level_data in INITIAL_LEVELS:
            session.add(Level(**level_data))
        await session.commit()
        logger.info("Niveles iniciales insertados correctamente.")
    else:
        logger.info("Los niveles ya existen en la base de datos.")

    # Insertar insignias
    result_badges = await session.execute(select(Badge))
    if not result_badges.scalars().first():
        logger.info("No se encontraron insignias, insertando insignias iniciales...")
        for badge_data in INITIAL_BADGES:
            session.add(Badge(**badge_data))
        await session.commit()
        logger.info("Insignias iniciales insertadas correctamente.")
    else:
        logger.info("Las insignias ya existen en la base de datos.")

    # Insertar recompensas
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
    """
    Proporciona una sesión de base de datos asíncrona.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
