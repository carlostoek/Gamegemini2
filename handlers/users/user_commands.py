# handlers/users/user_commands.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from database.models.user import User
from database.models.level import Level
from utils.logger import logger
from config.settings import settings
import json # Asegúrate de que json esté importado aquí para las insignias

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession, user: User):
    logger.info(f"Comando /start recibido de usuario: {user.username or user.first_name} (ID: {user.id})")
    welcome_message = (
        f"¡Hola, {user.first_name}! 👋\n\n"
        "¡Bienvenido al universo exclusivo de [Nombre de tu Canal/Comunidad]! 🚀\n\n"
        "Soy tu asistente personal, diseñado para enriquecer tu experiencia aquí. "
        "Conmigo podrás:\n\n"
        "✨ **Acumular puntos** por tu actividad y permanencia.\n"
        "🏆 **Subir de nivel** y desbloquear beneficios exclusivos.\n"
        "🏅 **Ganar insignias** por tus logros.\n"
        "🎁 **Canjear puntos** por recompensas increíbles en nuestro catálogo VIP.\n\n"
        "Estoy aquí para guiarte en cada paso. Si tienes dudas, usa /help para ver mis comandos.\n\n"
        "¡Prepárate para una experiencia única! 🎉"
    )
    await message.answer(welcome_message)

@router.message(Command("help"))
async def cmd_help(message: types.Message, session: AsyncSession, user: User):
    logger.info(f"Comando /help recibido de usuario: {user.username or user.first_name} (ID: {user.id})")
    help_message = (
        "Aquí tienes una lista de comandos disponibles:\n\n"
        "📚 **/start** - Inicia el bot y recibe un mensaje de bienvenida.\n"
        "🆘 **/help** - Muestra esta lista de comandos.\n"
        "📊 **/status** - Consulta tu nivel actual, puntos, insignias y próxima recompensa de permanencia.\n"
        "🛒 **/shop** - Explora el catálogo de recompensas disponibles para canjear con tus puntos.\n"
        "💰 **/points** - Reclama tus puntos diarios por permanencia (una vez cada 24 horas).\n"
        "🎁 **/myrewards** - Ve las recompensas que has canjeado.\n\n"
        "¡Estamos aquí para ayudarte a sacar el máximo provecho de nuestra comunidad! 😊"
    )
    await message.answer(help_message)

@router.message(Command("status"))
async def cmd_status(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /status.
    """
    logger.info(f"Comando /status recibido de usuario: {user.username or user.first_name} (ID: {user.id})")

    # Cargar el nombre del nivel
    level_query = await session.execute(
        select(Level).filter_by(id=user.level_id)
    )
    level = level_query.scalars().first()
    level_name = level.name if level else "Desconocido"

    # Lógica para las insignias
    try:
        # Aseguramos que user.badges_json sea una cadena válida antes de intentar parsearla
        user_badges_raw = user.badges_json if user.badges_json is not None else "[]"
        user_badges = json.loads(user_badges_raw)
        badges_list = ", ".join([badge['name'] for badge in user_badges]) if user_badges else "Ninguna"
    except json.JSONDecodeError:
        logger.error(f"Error al decodificar insignias para usuario {user.id}: {user.badges_json}")
        badges_list = "Error al cargar insignias"
    except Exception as e:
        logger.error(f"Error inesperado al procesar insignias para usuario {user.id}: {e}")
        badges_list = "Error al cargar insignias"

    status_message = (
        f"**Estado de {user.first_name}:**\n"
        f"Nivel: **{level_name}** ({user.points} puntos)\n"
        f"Insignias: {badges_list}\n"
        f"Interacciones hoy: {user.interactions_count}\n"
        f"Última interacción: {user.last_interaction_at.strftime('%Y-%m-%d %H:%M:%S') if user.last_interaction_at else 'N/A'}\n"
        f"Últimos puntos diarios: {user.last_daily_points_claim.strftime('%Y-%m-%d %H:%M:%S') if user.last_daily_points_claim else 'Nunca'}\n"
        f"Es Admin: {'Sí' if user.is_admin else 'No'}\n"
    )
    await message.answer(status_message)

@router.message(Command("admin"))
async def cmd_admin_panel(message: types.Message, session: AsyncSession, user: User):
    """
    Muestra el panel de administración si el usuario es un administrador.
    """
    if user.id in settings.ADMIN_IDS:
        admin_message = (
            "Panel de Administración:\n\n"
            "Puedes gestionar usuarios, recompensas y configuraciones.\n"
            "Comandos disponibles para administradores (ejemplo):\n"
            "/add_points <user_id> <amount>\n"
            "/set_level <user_id> <level_id>\n"
            "/add_badge <user_id> <badge_id>\n"
        )
    else:
        admin_message = "Acceso denegado. No tienes permisos de administrador."
    await message.answer(admin_message)
