# utils/formatter.py
from database.models.level import Level
from database.models.user import User
from database.models.badge import Badge
from database.models.reward import Reward # Nueva importación
from typing import Optional, List

def format_progress_bar(current_points: int, next_level_min_points: int, segment_length: int = 10) -> str:
    """
    Genera una barra de progreso visual.
    current_points: Puntos actuales del usuario dentro del segmento de nivel.
    next_level_min_points: Puntos necesarios para el siguiente nivel desde el inicio del segmento.
    segment_length: Longitud total de la barra (caracteres).
    """
    if segment_length <= 0:
        return ""

    if next_level_min_points <= 0: # Evitar división por cero
        progress_percentage = 1.0
    else:
        progress_percentage = min(1.0, current_points / next_level_min_points)

    filled_length = int(segment_length * progress_percentage)
    empty_length = segment_length - filled_length

    bar = "█" * filled_length + "░" * empty_length
    return f"[{bar}]"

def format_user_status(user: User, current_level: Level, next_level: Optional[Level], points_to_next_level: int, user_badges: List[Badge]) -> str:
    """
    Formatea el mensaje de estado del usuario para el comando /mispuntos.
    Ahora incluye las insignias desbloqueadas.
    """
    username_display = f"@{user.username}" if user.username else user.first_name or "Usuario VIP"
    
    status_message = (
        f"🌟 **Estado de {username_display}** 🌟\n\n"
        f"💎 Puntos: `{user.points}`\n"
        f"✨ Nivel actual: **{current_level.name}**\n"
    )

    if next_level:
        target_points_segment = next_level.min_points - current_level.min_points if current_level.min_points is not None else next_level.min_points
        current_segment_points = user.points - current_level.min_points if current_level.min_points is not None else user.points
        
        progress_bar = format_progress_bar(current_segment_points, target_points_segment)
        
        status_message += (
            f"📈 Progreso al siguiente nivel (`{next_level.name}`):\n"
            f"{progress_bar} `{points_to_next_level}` puntos restantes\n\n"
        )
    else:
        status_message += (
            f"🎉 ¡Has alcanzado el nivel máximo: **Leyenda Suprema**! 🎉\n\n"
        )

    status_message += "🏅 **Tus Insignias:**\n"
    if user_badges:
        badges_list = [f"{badge.icon} {badge.name}" for badge in user_badges]
        status_message += "\n".join(badges_list) + "\n\n"
    else:
        status_message += "Aún no tienes insignias. ¡Sigue interactuando para desbloquearlas!\n\n"

    status_message += "🚀 Usa `/ranking` para ver tu posición."
    
    return status_message

def format_ranking_entry_anonymous(rank: int, user: User, level: Level, current_user_id: int) -> str:
    """
    Formatea una entrada del ranking de forma anónima, mostrando el nombre completo
    solo para el usuario que consulta.
    """
    if user.id == current_user_id:
        display_name = f"@{user.username}" if user.username else user.first_name or "Tú"
    else:
        # Anonimizar el nombre de usuario
        if user.username:
            display_name = f"{user.username[0]}****"
        elif user.first_name:
            display_name = f"{user.first_name[0]}****"
        else:
            display_name = "Anónimo****" # Fallback si no hay ni username ni first_name

    return f"{rank}. **{display_name}** - `{user.points}` Pts ({level.name})"

def format_reward_details(reward: Reward) -> str:
    """
    Formatea los detalles de una recompensa para el catálogo.
    """
    stock_info = f"📦 Stock: {'Ilimitado' if reward.stock == -1 else reward.stock}"
    return (
        f"**{reward.name}**\n"
        f"  _Costo:_ `{reward.cost_points}` Puntos\n"
        f"  _Descripción:_ {reward.description}\n"
        f"  {stock_info}"
    )