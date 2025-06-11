# handlers/users/user_commands.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from database.models.user import User
from database.models.level import Level
from database.models.badge import Badge
from database.models.purchase import Purchase
from services.points_service import PointsService
from services.level_service import LevelService
from services.badge_service import BadgeService
from services.ranking_service import RankingService
from utils.logger import logger
from utils.formatter import format_user_status, format_ranking_entry_anonymous
from config.settings import settings
import json

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
        "🛒 **/catalogo** - Explora el catálogo de recompensas disponibles para canjear con tus puntos.\n"
        "💰 **/points** - Reclama tus puntos diarios por permanencia (una vez cada 24 horas).\n"
        "🎁 **/myrewards** - Ve las recompensas que has canjeado.\n"
        "🏆 **/ranking** - Ve tu posición en el ranking de la comunidad.\n\n"
        "¡Estamos aquí para ayudarte a sacar el máximo provecho de nuestra comunidad! 😊"
    )
    await message.answer(help_message)

@router.message(Command("status"))
async def cmd_status(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /status.
    """
    logger.info(f"Comando /status recibido de usuario: {user.username or user.first_name} (ID: {user.id})")

    try:
        # Obtener servicios necesarios
        level_service = LevelService(session)
        badge_service = BadgeService(session)
        
        # Cargar el nivel actual
        current_level = await level_service.get_level_by_id(user.level_id)
        if not current_level:
            current_level = await level_service.get_level_by_id(1)  # Fallback al nivel 1
        
        # Obtener información del siguiente nivel
        next_level, points_to_next_level = await level_service.get_next_level_info(user.points)
        
        # Cargar insignias del usuario
        try:
            user_badges_raw = user.badges_json if user.badges_json is not None else "[]"
            user_badges_data = json.loads(user_badges_raw)
            # Convertir a objetos Badge si es necesario, por ahora usar los datos JSON
            badges_list = ", ".join([badge['name'] for badge in user_badges_data]) if user_badges_data else "Ninguna"
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar insignias para usuario {user.id}: {user.badges_json}")
            badges_list = "Error al cargar insignias"
        except Exception as e:
            logger.error(f"Error inesperado al procesar insignias para usuario {user.id}: {e}")
            badges_list = "Error al cargar insignias"

        # Formatear mensaje de estado
        status_message = (
            f"**Estado de {user.first_name}:**\n\n"
            f"💎 **Puntos:** {user.points}\n"
            f"✨ **Nivel:** {current_level.name}\n"
            f"🏅 **Insignias:** {badges_list}\n"
            f"📈 **Interacciones hoy:** {user.interactions_count}\n"
        )
        
        if next_level:
            status_message += f"🎯 **Siguiente nivel:** {next_level.name} ({points_to_next_level} puntos restantes)\n"
        else:
            status_message += "🎉 **¡Has alcanzado el nivel máximo!**\n"
            
        status_message += (
            f"⏰ **Última interacción:** {user.last_interaction_at.strftime('%Y-%m-%d %H:%M:%S') if user.last_interaction_at else 'N/A'}\n"
            f"💰 **Últimos puntos diarios:** {user.last_daily_points_claim.strftime('%Y-%m-%d %H:%M:%S') if user.last_daily_points_claim else 'Nunca'}\n"
        )
        
        if user.is_admin:
            status_message += "👑 **Rol:** Administrador\n"
            
        await message.answer(status_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error en comando /status para usuario {user.id}: {e}", exc_info=True)
        await message.answer("❌ Ocurrió un error al obtener tu estado. Por favor, intenta de nuevo más tarde.")

@router.message(Command("points"))
async def cmd_claim_daily_points(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /points - Reclama puntos diarios por permanencia.
    """
    logger.info(f"Comando /points recibido de usuario: {user.username or user.first_name} (ID: {user.id})")
    
    try:
        points_service = PointsService(session)
        now = datetime.now()
        
        # Verificar si ya reclamó puntos hoy
        if user.last_daily_points_claim:
            time_since_last_claim = now - user.last_daily_points_claim
            if time_since_last_claim < timedelta(hours=24):
                hours_remaining = 24 - int(time_since_last_claim.total_seconds() / 3600)
                await message.answer(
                    f"⏰ Ya reclamaste tus puntos diarios hoy.\n"
                    f"Podrás reclamar nuevamente en {hours_remaining} horas."
                )
                return
        
        # Otorgar puntos diarios (10 puntos base)
        daily_points = 10
        await points_service.add_points(user, daily_points, "Puntos diarios por permanencia")
        
        # Actualizar la fecha de último reclamo
        user.last_daily_points_claim = now
        await session.commit()
        await session.refresh(user)
        
        success_message = (
            f"🎉 **¡Puntos diarios reclamados!**\n\n"
            f"💰 Has ganado **{daily_points} puntos** por tu permanencia diaria.\n"
            f"💎 **Puntos totales:** {user.points}\n\n"
            f"¡Vuelve mañana para reclamar más puntos! 🚀"
        )
        
        await message.answer(success_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error en comando /points para usuario {user.id}: {e}", exc_info=True)
        await message.answer("❌ Ocurrió un error al reclamar tus puntos. Por favor, intenta de nuevo más tarde.")

@router.message(Command("myrewards"))
async def cmd_my_rewards(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /myrewards - Muestra las recompensas canjeadas por el usuario.
    """
    logger.info(f"Comando /myrewards recibido de usuario: {user.username or user.first_name} (ID: {user.id})")
    
    try:
        # Obtener las compras/canjes del usuario
        result = await session.execute(
            select(Purchase)
            .filter(Purchase.user_id == user.id)
            .order_by(Purchase.purchase_date.desc())
        )
        purchases = result.scalars().all()
        
        if not purchases:
            await message.answer(
                "🎁 **Mis Recompensas**\n\n"
                "Aún no has canjeado ninguna recompensa.\n"
                "Usa /catalogo para ver las recompensas disponibles y empieza a acumular puntos! 🚀"
            )
            return
        
        rewards_message = "🎁 **Mis Recompensas Canjeadas**\n\n"
        
        for i, purchase in enumerate(purchases[:10], 1):  # Mostrar últimas 10
            date_str = purchase.purchase_date.strftime('%Y-%m-%d')
            rewards_message += (
                f"**{i}.** {purchase.description or 'Recompensa'}\n"
                f"   💰 Costo: {purchase.points_awarded} puntos\n"
                f"   📅 Fecha: {date_str}\n\n"
            )
        
        if len(purchases) > 10:
            rewards_message += f"... y {len(purchases) - 10} recompensas más.\n\n"
            
        rewards_message += (
            f"💎 **Total de puntos gastados:** {sum(p.points_awarded for p in purchases)}\n"
            f"🛒 **Total de canjes:** {len(purchases)}"
        )
        
        await message.answer(rewards_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error en comando /myrewards para usuario {user.id}: {e}", exc_info=True)
        await message.answer("❌ Ocurrió un error al obtener tus recompensas. Por favor, intenta de nuevo más tarde.")

@router.message(Command("ranking"))
async def cmd_ranking(message: types.Message, session: AsyncSession, user: User):
    """
    Handler para el comando /ranking - Muestra el ranking de usuarios.
    """
    logger.info(f"Comando /ranking recibido de usuario: {user.username or user.first_name} (ID: {user.id})")
    
    try:
        ranking_service = RankingService(session)
        
        # Obtener top 10 usuarios
        top_users = await ranking_service.get_top_users(10)
        
        if not top_users:
            await message.answer("📊 El ranking está vacío por el momento.")
            return
        
        # Obtener la posición del usuario actual
        user_rank = await ranking_service.get_user_rank(user.id)
        
        ranking_message = "🏆 **Ranking de la Comunidad VIP** 🏆\n\n"
        
        for i, (ranked_user, level) in enumerate(top_users, 1):
            entry = format_ranking_entry_anonymous(i, ranked_user, level, user.id)
            ranking_message += f"{entry}\n"
        
        ranking_message += "\n" + "─" * 30 + "\n"
        
        if user_rank:
            if user_rank <= 10:
                ranking_message += f"🎯 **Tu posición:** Ya estás en el Top 10! (#{user_rank})"
            else:
                ranking_message += f"🎯 **Tu posición:** #{user_rank}"
        else:
            ranking_message += "🎯 **Tu posición:** No clasificado aún"
            
        ranking_message += f"\n💎 **Tus puntos:** {user.points}"
        
        await message.answer(ranking_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error en comando /ranking para usuario {user.id}: {e}", exc_info=True)
        await message.answer("❌ Ocurrió un error al obtener el ranking. Por favor, intenta de nuevo más tarde.")

@router.message(Command("admin"))
async def cmd_admin_panel(message: types.Message, session: AsyncSession, user: User):
    """
    Muestra el panel de administración si el usuario es un administrador.
    """
    if user.id in settings.ADMIN_IDS or user.is_admin:
        admin_message = (
            "👑 **Panel de Administración** 👑\n\n"
            "Comandos disponibles:\n\n"
            "💰 `/sumarpuntos [user_id] [monto] [descripción]`\n"
            "   - Registra una compra y asigna puntos\n"
            "   - Ej: `/sumarpuntos 123456789 350.00 Acceso Canal VIP`\n\n"
            "📊 **Estadísticas del sistema:**\n"
            f"👥 Usuarios registrados: En desarrollo\n"
            f"🎁 Recompensas activas: En desarrollo\n"
            f"💎 Puntos totales distribuidos: En desarrollo"
        )
    else:
        admin_message = "🚫 Acceso denegado. No tienes permisos de administrador."
    
    await message.answer(admin_message, parse_mode="Markdown")