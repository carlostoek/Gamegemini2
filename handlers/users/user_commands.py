# handlers/users/user_commands.py
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.user_service import UserService
from services.level_service import LevelService
from services.badge_service import BadgeService
from services.ranking_service import RankingService # Nueva importación
from utils.formatter import format_user_status, format_ranking_entry_anonymous # Modificación aquí
from utils.logger import logger

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, db_user: User, session: AsyncSession):
    """
    Handler para el comando /start.
    Crea un nuevo usuario si no existe y da la bienvenida.
    """
    if db_user.is_new_user:
        welcome_message = (
            f"🎉 ¡Bienvenido/a al programa de recompensas, {message.from_user.first_name}! 🎉\n"
            "Con cada interacción, compra y tu permanencia en el canal, ganarás **Puntos Íntimos**.\n\n"
            "Estos puntos te permitirán subir de **Nivel** y desbloquear **Insignias** exclusivas. "
            "¡Pronto podrás canjear tus puntos por recompensas increíbles en el **Catálogo VIP**!\n\n"
            "Empieza a ganar puntos reaccionando a las publicaciones, participando en encuestas y "
            "mucho más. ¡Usa `/mispuntos` para ver tu progreso!"
        )
        await message.reply(welcome_message)
        logger.info(f"Nuevo usuario registrado: {message.from_user.id} ({message.from_user.username})")
    else:
        await message.reply(f"¡Hola de nuevo, {message.from_user.first_name}! Sigue acumulando puntos y explorando el canal. Usa `/mispuntos` para revisar tu estado.")
        logger.info(f"Usuario existente {message.from_user.id} ({message.from_user.username}) usó /start.")

@router.message(F.text == "/mispuntos")
async def cmd_my_points(message: Message, db_user: User, session: AsyncSession):
    """
    Handler para el comando /mispuntos.
    Muestra los puntos, nivel actual, progreso hacia el siguiente nivel y insignias.
    """
    logger.info(f"Usuario {message.from_user.id} ({db_user.username}) usó /mispuntos")

    user_service = UserService(session) # No estrictamente necesario aquí si db_user ya está cargado por middleware
    level_service = LevelService(session)
    badge_service = BadgeService(session) # Instanciar BadgeService

    current_level_obj = await level_service.get_level_by_id(db_user.level)
    if not current_level_obj:
        logger.error(f"Nivel {db_user.level} no encontrado para usuario {db_user.id}.")
        await message.reply("Lo siento, no pude cargar tu información de nivel. Intenta de nuevo más tarde.")
        return

    next_level_obj, points_to_next_level = await level_service.get_next_level_info(db_user.points)
    user_badges = await badge_service.get_user_badges(db_user) # Obtener las insignias del usuario

    status_message = format_user_status(db_user, current_level_obj, next_level_obj, points_to_next_level, user_badges)
    await message.reply(status_message, parse_mode="Markdown")

@router.message(F.text == "/ranking")
async def cmd_ranking(message: Message, db_user: User, session: AsyncSession):
    """
    Handler para el comando /ranking.
    Muestra el top 10 de usuarios, con nombres anonimizados, excepto el propio usuario.
    """
    logger.info(f"Usuario {message.from_user.id} ({db_user.username}) usó /ranking.")

    ranking_service = RankingService(session)
    top_users_data = await ranking_service.get_top_users(limit=10)
    user_rank = await ranking_service.get_user_rank(db_user.id)

    ranking_message = "🏆 **TOP 10 de Puntos Íntimos** 🏆\n\n"

    if not top_users_data:
        ranking_message += "Aún no hay suficientes datos para mostrar un ranking. ¡Sé el primero en ganar puntos!\n"
    else:
        for i, (user, level) in enumerate(top_users_data):
            ranking_message += format_ranking_entry_anonymous(i + 1, user, level, db_user.id) + "\n"

    if user_rank:
        ranking_message += f"\nTu posición: **#{user_rank}**"
    else:
        ranking_message += "\nActualmente no estás en el Top 10. ¡Sigue sumando puntos para subir!"

    await message.reply(ranking_message, parse_mode="Markdown")