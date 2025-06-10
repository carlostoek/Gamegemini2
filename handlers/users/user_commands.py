# handlers/users/user_commands.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func # Para usar funciones SQL como func.now()

from database.models.user import User
from database.models.level import Level # Para cargar el nombre del nivel
from utils.logger import logger
from config.settings import settings

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /start.
    """
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
    """
    Handler para el comando /help.
    """
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

    # --- Lógica original COMENTADA TEMPORALMENTE para depuración ---
    # level_query = await session.execute(
    #     select(Level).filter_by(id=user.level_id)
    # )
    # level = level_query.scalars().first()
    # level_name = level.name if level else "Desconocido"
    #
    # import json
    # try:
    #     user_badges = json.loads(user.badges_json) if user.badges_json else []
    #     badges_list = ", ".join([badge['name'] for badge in user_badges]) if user_badges else "Ninguna"
    # except json.JSONDecodeError:
    #     badges_list = "Error al cargar insignias"
    # --- FIN DE LÓGICA COMENTADA ---

    # Mensaje de prueba simple
    status_message = (
        f"**¡Hola, {user.first_name}!**\n"
        "Este es un mensaje de prueba para /status. ¡El comando funciona si ves esto!"
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
