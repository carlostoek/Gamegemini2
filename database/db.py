# database/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base # Importa declarative_base directamente aquí
from contextlib import asynccontextmanager
from sqlalchemy.future import select

# Asumo que Base.metadata es accesible aquí, si no, lo más fácil es definir Base aquí
# Si quieres mantener Base en base_model.py, asegúrate de que base_model.py
# tenga: from sqlalchemy.orm import declarative_base; Base = declarative_base()
# y que esa Base sea la que todos tus modelos heredan.
# Por simplicidad y para asegurar que Base se inicialice correctamente para el engine:
# Define la base declarativa para tus modelos SQLAlchemy aquí mismo si no hay una razón fuerte para que este en otro archivo.
# Si el_juego_del_divan/database/base_model.py existe y solo contiene 'Base = declarative_base()',
# podrías considerar mover esa línea aquí para consolidar.
# Por ahora, mantendremos la importación asumiendo que es correcta.
from database.base_model import Base # Si base_model.py solo contiene 'Base = declarative_base()'

from config.settings import settings
from utils.logger import logger

# IMPORTANTE: Asegúrate de que todos tus modelos sean importados aquí
# para que Base.metadata.create_all los descubra y cree sus tablas.
# Los prefijos de importación deben coincidir con tu estructura de paquetes (el_juego_del_divan.database.models).
# Aquí los he ajustado para que la importación funcione desde db.py dentro de el_juego_del_divan/database/
from database.models.user import User
from database.models.level import Level, INITIAL_LEVELS
from database.models.badge import Badge, INITIAL_BADGES
from database.models.purchase import Purchase
from database.models.reward import Reward, INITIAL_REWARDS
from database.models.mission import Mission # Asegúrate de importar todos tus modelos

DATABASE_URL = settings.DATABASE_URL

# Crear el engine asíncrono
# *** SOLUCIÓN CLAVE: future=True es fundamental para SQLAlchemy 2.0 y evitar MissingGreenlet ***
# echo=True es útil para depuración, mostrará las consultas SQL en los logs.
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Usa async_sessionmaker para el manejo asíncrono de sesiones
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
    """
    logger.info("Inicializando la base de datos...")
    async with async_engine.begin() as conn:
        # run_sync es necesario para ejecutar Base.metadata.create_all de forma síncrona
        # dentro de un contexto asíncrono sin bloquear el bucle de eventos.
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
    Utiliza async_session_maker directamente.
    """
    async with async_session_maker() as session:
        yield session

# =========================================================================
# Considera si necesitas un if __name__ == "__main__": aquí.
# Si init_db() y insert_initial_data() ya se llaman desde bot.py al iniciar,
# entonces no necesitas este bloque.
# =========================================================================
# if __name__ == "__main__":
#     import asyncio
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
