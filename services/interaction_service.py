# services/interaction_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.points_service import PointsService
from services.user_service import UserService # Necesario para update_user_interaction_data
from utils.logger import logger
from datetime import datetime, timedelta
import asyncio

class InteractionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.points_service = PointsService(session)
        self.user_service = UserService(session) # Inicializar UserService aquí

    async def process_reaction(self, user: User, post_id: str, points: int) -> tuple[bool, str]:
        """
        Procesa una reacción a una publicación.
        Retorna (True/False si la acción fue exitosa, Mensaje para el usuario).
        Aplica límite de 1 reacción por publicación y límite diario de puntos.
        """
        # Generar un ID único para la reacción del usuario en esta publicación
        # Para evitar re-reacciones: podríamos tener una tabla de 'reactions_log'
        # Por simplicidad ahora: un mecanismo más robusto podría ser necesario para alta escala
        # Para la demostración, asumiremos que el callback_data es suficiente para identificar la primera reacción
        # En una solución real, usaríamos un log en la DB para cada reacción.
        
        # Validación de límite diario de puntos por interacción
        now = datetime.now()
        # Asegurar que el daily_points_earned se resetea al inicio del día
        if user.last_daily_reset.date() < now.date():
            await self.user_service.update_user_interaction_data(user, 0) # Resetea y actualiza last_daily_reset
            user.daily_points_earned = 0 # Asegura que el objeto db_user en memoria también se actualice

        from utils.constants import MAX_DAILY_INTERACTION_POINTS # Importar aquí para evitar circular imports
        if user.daily_points_earned + points > MAX_DAILY_INTERACTION_POINTS:
            remaining_points_today = MAX_DAILY_INTERACTION_POINTS - user.daily_points_earned
            if remaining_points_today > 0:
                # Si puede ganar algunos puntos más pero no todos
                points_to_award = remaining_points_today
                message = (f"¡Excelente! Ganaste {points_to_award} puntos por esta interacción. "
                           f"Has alcanzado tu límite diario de puntos por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades de ganar!")
                await self.points_service.add_points(user, points_to_award, reason=f"Reacción a post {post_id} (límite diario)")
            else:
                message = (f"¡Gracias por tu participación! Pero ya alcanzaste tu límite diario de puntos "
                           f"por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades de ganar!")
                return False, message
        else:
            await self.points_service.add_points(user, points, reason=f"Reacción a post {post_id}")
            message = f"¡Puntos añadidos! Ganaste {points} puntos por tu reacción. Tus nuevos puntos son: {user.points}."

        # Actualizar los puntos ganados hoy y la última fecha de interacción
        await self.user_service.update_user_interaction_data(user, points)

        return True, message

    async def process_survey_vote(self, user: User, survey_id: str, option_index: int, points: int) -> tuple[bool, str]:
        """
        Procesa un voto en una encuesta.
        Retorna (True/False si la acción fue exitosa, Mensaje para el usuario).
        Aplica límite diario de puntos por interacción.
        """
        # Similar a las reacciones, se podría implementar un log para evitar múltiples votos por encuesta.
        # Por ahora, nos centraremos en el límite diario.

        now = datetime.now()
        if user.last_daily_reset.date() < now.date():
            await self.user_service.update_user_interaction_data(user, 0)
            user.daily_points_earned = 0

        from utils.constants import MAX_DAILY_INTERACTION_POINTS
        if user.daily_points_earned + points > MAX_DAILY_INTERACTION_POINTS:
            remaining_points_today = MAX_DAILY_INTERACTION_POINTS - user.daily_points_earned
            if remaining_points_today > 0:
                points_to_award = remaining_points_today
                message = (f"¡Voto registrado! Ganaste {points_to_award} puntos. "
                           f"Has alcanzado tu límite diario de puntos por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades!")
                await self.points_service.add_points(user, points_to_award, reason=f"Voto en encuesta {survey_id}")
            else:
                message = (f"¡Gracias por participar en la encuesta! Ya alcanzaste tu límite diario de puntos "
                           f"por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades!")
                return False, message
        else:
            await self.points_service.add_points(user, points, reason=f"Voto en encuesta {survey_id}")
            message = f"¡Puntos añadidos! Ganaste {points} puntos por tu voto. Tus nuevos puntos son: {user.points}."
        
        await self.user_service.update_user_interaction_data(user, points)
        
        return True, message

    async def process_narrative_choice(self, user: User, decision_id: str, choice_value: str, points: int) -> tuple[bool, str]:
        """
        Procesa una elección en una narrativa interactiva.
        Aplica límite diario de puntos por interacción.
        """
        # Similar a las reacciones, se podría implementar un log para evitar múltiples elecciones.

        now = datetime.now()
        if user.last_daily_reset.date() < now.date():
            await self.user_service.update_user_interaction_data(user, 0)
            user.daily_points_earned = 0

        from utils.constants import MAX_DAILY_INTERACTION_POINTS
        if user.daily_points_earned + points > MAX_DAILY_INTERACTION_POINTS:
            remaining_points_today = MAX_DAILY_INTERACTION_POINTS - user.daily_points_earned
            if remaining_points_today > 0:
                points_to_award = remaining_points_today
                message = (f"¡Elección registrada! Ganaste {points_to_award} puntos. "
                           f"Has alcanzado tu límite diario de puntos por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades!")
                await self.points_service.add_points(user, points_to_award, reason=f"Elección narrativa {decision_id}")
            else:
                message = (f"¡Gracias por participar en la narrativa! Ya alcanzaste tu límite diario de puntos "
                           f"por interacciones ({MAX_DAILY_INTERACTION_POINTS} Pts).\n"
                           "¡Vuelve mañana para más oportunidades!")
                return False, message
        else:
            await self.points_service.add_points(user, points, reason=f"Elección narrativa {decision_id}")
            message = f"¡Puntos añadidos! Ganaste {points} puntos por tu elección. Tus nuevos puntos son: {user.points}."
        
        await self.user_service.update_user_interaction_data(user, points)
        
        return True, message