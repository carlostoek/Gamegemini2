# el_juego_del_divan/database/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from sqlalchemy.future import select
import asyncio # Necesario si vas a usar asyncio.run() en un if __name__ == "__main__" block

from el_juego_del_divan.config.settings import settings
from el_juego_del_divan.utils.logger import logger

# Define la base declarativa para tus modelos SQLAlchemy.
# Se mantiene aquí por convención si solo base_model.py contiene 'Base = declarative_base()'.
# Si prefieres que solo base_model.py contenga la definición, este import es correcto.
from database.base_model import Base

# URL de conexión a la base de datos desde tus settings
DATABASE_URL = settings.DATABASE_URL

# Crea el motor de base de datos asíncrono
# *** CRUCIAL: future=True es esencial para SQLAlchemy 2.0 y el manejo de contextos asíncronos. ***
# echo=True es útil para depuración, muestra las consultas SQL en los logs.
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Crea un generador de sesiones asíncronas. Esto reemplaza a 'AsyncSessionLocal'.
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False, # Generalmente False para manejo transaccional explícito
    autoflush=False,  # Generalmente False para mejor control
    expire_on_commit=False, # No expira objetos después del commit, útil para mantenerlos en la sesión
)

async def init_db():
    """
    Inicializa la base de datos: crea todas las tablas definidas en Base.
    Esta función debe ser llamada al inicio del bot (ej. en bot.py o main.py).
    """
    logger.info("Inicializando la base de datos...")
    async with async_engine.begin() as conn:
        # run_sync es necesario para ejecutar operaciones de metadata de forma síncrona
        # dentro de un contexto asíncrono sin bloquear el bucle de eventos.
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos inicializada correctamente.")

# IMPORTANTE: Asegúrate de que todos tus modelos sean importados aquí
# para que Base.metadata.create_all los descubra y cree sus tablas.
# Los prefijos de importación deben coincidir con tu estructura de paquetes.
from database.models.user import User
from database.models.level import Level, INITIAL_LEVELS
from database.models.badge import Badge, INITIAL_BADGES
from database.models.purchase import Purchase
from database.models.reward import Reward, INITIAL_REWARDS
from database.models.mission import Mission # Asegúrate de importar todos tus modelos aquí

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
    Utiliza async_session_maker directamente.
    """
    async with async_session_maker() as session:
        yield session

# Bloque para inicialización/seed si se ejecuta el script directamente.
# Normalmente, estas funciones se llaman desde bot.py al iniciar.
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
