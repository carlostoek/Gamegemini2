# services/permanence_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from database.models.user import User
from services.points_service import PointsService
from services.badge_service import BadgeService # Se usará más adelante para insignias
from utils.logger import logger
from utils.constants import (
    POINTS_PER_WEEK, WEEKLY_STREAK_BONUS, MAX_WEEKLY_STREAK_BONUS,
    POINTS_PER_MONTH, MILESTONE_6_MONTHS_POINTS, MILESTONE_1_YEAR_POINTS,
    BADGE_VETERAN_INTIMO # Para la insignia del hito de 6 meses
)
from aiogram import Bot

class PermanenceService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.points_service = PointsService(session)
        self.badge_service = BadgeService(session) # Se inicializa para uso futuro

    async def award_weekly_permanence_points(self) -> int:
        """
        Otorga puntos semanales de permanencia a todos los usuarios.
        También maneja las rachas y los hitos mensuales/anuales.
        """
        users = await self.session.execute(select(User))
        awarded_count = 0
        now = datetime.now()

        for user in users.scalars().all():
            # Puntos Semanales y Bonificación de Racha
            # Calcula cuántas semanas han pasado desde el último chequeo
            weeks_since_last_check = (now - user.last_permanence_check).days // 7

            if weeks_since_last_check >= 1:
                # Si ha pasado al menos una semana desde el último chequeo
                points_to_award_weekly = POINTS_PER_WEEK
                
                # Calcular bonus por racha
                current_streak_bonus = min(user.weekly_streak, MAX_WEEKLY_STREAK_BONUS)
                points_to_award_weekly += current_streak_bonus
                user.weekly_streak += 1 # Incrementa la racha si se cumplen las semanas

                await self.points_service.add_points(user, points_to_award_weekly, "Permanencia semanal")
                logger.info(f"Usuario {user.id}: {points_to_award_weekly} puntos por permanencia semanal (Racha: {user.weekly_streak}).")
                
                # Actualizar la fecha del último chequeo para reflejar que la semana actual ya fue premiada
                # Para evitar recompensar la misma semana múltiples veces en un solo chequeo diario.
                # Se puede ajustar para que el chequeo sea 'exactamente' semanal desde join_date
                # pero para el propósito de un job diario que actualiza semanalmente, esto funciona.
                user.last_permanence_check = now # Considera el día de la ejecución como el fin de la semana premiada

                awarded_count += 1
                
                # Puntos Mensuales (se calcula por separado para evitar duplicados si la semana es parte de un mes)
                # Verifica si ha pasado un mes completo desde la fecha de ingreso o desde el último bonus mensual
                # Una lógica más robusta sería llevar un campo `last_monthly_bonus_date`
                # Por simplicidad ahora, si la diferencia en meses es significativa:
                months_in_channel = (now.year - user.join_date.year) * 12 + (now.month - user.join_date.month)
                
                # Ejemplo de un chequeo mensual más directo y controlable:
                # Si el usuario ingresó el día X, premiarlo cada día X del mes.
                if user.join_date.day == now.day: # Se ejecuta en el mismo día del mes de ingreso
                     if user.join_date.month != now.month or user.join_date.year != now.year: # Asegura que sea un mes diferente al de ingreso
                         if (now.month - user.join_date.month) % 1 == 0: # Cada mes
                            # Esta lógica es más compleja si queremos ser precisos con el mes
                            # Por ahora, un enfoque simplificado: si ha pasado un mes completo
                            if (now - user.join_date).days >= 30 and (now - user.last_permanence_check).days >= 30: # Evitar doble conteo semanal
                                await self.points_service.add_points(user, POINTS_PER_MONTH, "Permanencia mensual")
                                logger.info(f"Usuario {user.id}: {POINTS_PER_MONTH} puntos por permanencia mensual.")
                                # Considerar actualizar `last_monthly_bonus_date` en el modelo User

                # Hitos de Permanencia (se chequean una sola vez)
                total_days_in_channel = (now - user.join_date).days
                
                # Hito de 6 meses
                if total_days_in_channel >= 180 and BADGE_VETERAN_INTIMO not in user.badges:
                    await self.points_service.add_points(user, MILESTONE_6_MONTHS_POINTS, "Hito 6 meses")
                    await self.badge_service.award_badge(user, BADGE_VETERAN_INTIMO, "Veterano Íntimo")
                    await self._send_notification(user.id, f"🎉 ¡Felicidades! Has alcanzado el hito de 6 meses en el canal. Ganaste {MILESTONE_6_MONTHS_POINTS} puntos y la insignia '{BADGE_VETERAN_INTIMO}'.")
                    logger.info(f"Usuario {user.id}: Hito 6 meses alcanzado. +{MILESTONE_6_MONTHS_POINTS} puntos.")

                # Hito de 1 año
                if total_days_in_channel >= 365 and "veterano_anual" not in user.badges: # Asumiendo una insignia para 1 año
                    await self.points_service.add_points(user, MILESTONE_1_YEAR_POINTS, "Hito 1 año")
                    # Podrías crear una insignia BADGE_VETERAN_ANUAL
                    # await self.badge_service.award_badge(user, "veterano_anual", "Veterano Anual")
                    await self._send_notification(user.id, f"🌟 ¡Increíble! Llevas 1 año con nosotros. Ganaste {MILESTONE_1_YEAR_POINTS} puntos y contenido exclusivo.")
                    logger.info(f"Usuario {user.id}: Hito 1 año alcanzado. +{MILESTONE_1_YEAR_POINTS} puntos.")

                # Guardar los cambios en el usuario
                await self.session.commit()
                await self.session.refresh(user)
            else:
                # Si no ha pasado una semana completa, la racha se rompe
                # Esto es crucial para la lógica de racha. Si el job se ejecuta diariamente,
                # necesitamos saber si el usuario interactuó (o fue activo) en la última semana.
                # Para simplificar ahora, si `last_permanence_check` es muy antigua, se rompe.
                # Una racha más robusta necesitaría un registro de actividad diaria o semanal.
                
                # Si el sistema solo da puntos por permanencia y no requiere actividad activa,
                # entonces la racha solo se mantiene si el bot fue ejecutado y procesó al usuario.
                # Para este sistema, el 'last_permanence_check' se actualizará cuando se le otorguen puntos.
                # Si el usuario no fue premiado por x semanas (porque el bot no corrió, etc.),
                # la racha debería romperse aquí.
                
                # Por el momento, la racha simplemente progresa mientras se otorguen puntos semanalmente.
                pass

        return awarded_count

    async def _send_notification(self, user_id: int, message_text: str):
        """
        Envía una notificación al usuario.
        """
        try:
            await self.bot.send_message(user_id, message_text, parse_mode="Markdown")
            logger.info(f"Notificación enviada a usuario {user_id}: '{message_text[:50]}...'")
        except Exception as e:
            logger.error(f"No se pudo enviar notificación a usuario {user_id}: {e}", exc_info=True)