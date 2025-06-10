# handlers/users/user_commands.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from utils.logger import logger
from config.settings import settings # Para acceder a ADMIN_IDS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession, user: User): # <--- ¡CAMBIO AQUÍ! Añadimos 'user: User'
    """
    Handler para el comando /start.
    """
    # El objeto `User` ya es inyectado por UserMiddleware
    # Ahora podemos acceder a él directamente como 'user'
    
    # Aquí puedes usar 'user' para interactuar con la base de datos o mostrar info del usuario
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
async def cmd_help(message: types.Message, session: AsyncSession, user: User): # <--- ¡CAMBIO AQUÍ! Añadimos 'user: User'
    """
    Handler para el comando /help.
    """
    # Aquí también usamos 'user'
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
async def cmd_status(message: types.Message, session: AsyncSession, user: User): # <--- ¡CAMBIO AQUÍ! Añadimos 'user: User'
    """
    Handler para el comando /status.
    """
    logger.info(f"Comando /status recibido de usuario: {user.username or user.first_name} (ID: {user.id})")

    # Aquí iría la lógica para obtener la información detallada del usuario
    # y formatearla para el mensaje de estado.
    # Por ahora, un mensaje de prueba:
    status_message = (
        f"**Estado de {user.first_name}:**\n"
        f"Nivel: {user.level_id} (Nombre del nivel: [Cargar de DB])\n" # Tendrás que cargar el nombre del nivel real
        f"Puntos: {user.points}\n"
        f"Insignias: {user.badges_json} (Formatéalas mejor)\n"
        f"Interacciones hoy: {user.interactions_count}\n"
        f"Última interacción: {user.last_interaction_at.strftime('%Y-%m-%d %H:%M:%S') if user.last_interaction_at else 'N/A'}\n"
        f"Últimos puntos diarios: {user.last_daily_points_claim.strftime('%Y-%m-%d %H:%M:%S') if user.last_daily_points_claim else 'Nunca'}\n"
        f"Es Admin: {'Sí' if user.is_admin else 'No'}\n"
    )
    await message.answer(status_message)

# Handlers para administradores (ejemplo)
@router.message(Command("admin"))
async def cmd_admin_panel(message: types.Message, session: AsyncSession, user: User): # <--- ¡CAMBIO AQUÍ! Añadimos 'user: User'
    """
    Muestra el panel de administración si el usuario es un administrador.
    """
    if user.id in settings.ADMIN_IDS: # Acceder a settings.ADMIN_IDS directamente
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
