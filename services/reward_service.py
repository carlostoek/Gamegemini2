# services/reward_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from database.models.reward import Reward
from services.points_service import PointsService
from services.badge_service import BadgeService
from utils.logger import logger
from utils.constants import BADGE_PRIMER_CANJE # Para la insignia del primer canje
from typing import List, Optional
from aiogram import Bot

class RewardService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot # Para enviar notificaciones a usuarios/admins
        self.points_service = PointsService(session)
        self.badge_service = BadgeService(session)

    async def get_active_rewards(self) -> List[Reward]:
        """
        Obtiene todas las recompensas activas disponibles en el catálogo.
        """
        result = await self.session.execute(
            select(Reward).filter(Reward.is_active == True)
        )
        return result.scalars().all()

    async def get_reward_by_id(self, reward_id: int) -> Optional[Reward]:
        """
        Obtiene una recompensa por su ID.
        """
        result = await self.session.execute(
            select(Reward).filter(Reward.id == reward_id)
        )
        return result.scalars().first()

    async def redeem_reward(self, user: User, reward_id: int) -> tuple[bool, str]:
        """
        Procesa el canje de una recompensa por parte de un usuario.
        Retorna (True/False si el canje fue exitoso, Mensaje para el usuario).
        """
        reward = await self.get_reward_by_id(reward_id)

        if not reward or not reward.is_active:
            return False, "❌ La recompensa que intentas canjear no existe o no está activa."

        if reward.stock != -1 and reward.stock <= 0:
            return False, f"❌ Lo siento, la recompensa '{reward.name}' está agotada."

        if user.points < reward.cost_points:
            return False, (f"❌ No tienes suficientes puntos para canjear '{reward.name}'. "
                           f"Necesitas {reward.cost_points} puntos y solo tienes {user.points}.")

        # Procesar el canje
        try:
            # Restar puntos
            await self.points_service.subtract_points(user, reward.cost_points, f"Canje de recompensa: {reward.name}")
            
            # Disminuir stock si no es ilimitado
            if reward.stock != -1:
                reward.stock -= 1
                self.session.add(reward) # Guardar el cambio en el stock

            # Otorgar insignia de primer canje si aplica
            if BADGE_PRIMER_CANJE not in user.badges:
                await self.badge_service.award_badge(user, BADGE_PRIMER_CANJE, "Primer Canje")
                await self._send_notification_to_user(user.id, "🎉 ¡Felicidades! Has realizado tu primer canje y desbloqueado la insignia 'Primer Canje'.")

            await self.session.commit()
            await self.session.refresh(user) # Refrescar user para asegurar puntos actualizados
            
            # Notificar al administrador
            await self._notify_admin_about_redemption(user, reward)

            message_to_user = (
                f"✅ ¡Canje exitoso! Has canjeado '{reward.name}' por {reward.cost_points} puntos.\n"
                f"Tus puntos restantes son: {user.points}. Nos pondremos en contacto contigo pronto para coordinar la entrega/acceso de tu recompensa."
            )
            return True, message_to_user

        except Exception as e:
            await self.session.rollback() # Revertir la transacción si algo sale mal
            logger.error(f"Error al procesar canje de recompensa {reward_id} para usuario {user.id}: {e}", exc_info=True)
            return False, "❌ Ocurrió un error al intentar canjear la recompensa. Por favor, intenta de nuevo más tarde."

    async def _send_notification_to_user(self, user_id: int, message_text: str):
        """Envía una notificación al usuario."""
        try:
            await self.bot.send_message(user_id, message_text, parse_mode="Markdown")
            logger.info(f"Notificación de canje enviada a usuario {user_id}.")
        except Exception as e:
            logger.error(f"No se pudo enviar notificación de canje a usuario {user_id}: {e}", exc_info=True)

    async def _notify_admin_about_redemption(self, user: User, reward: Reward):
        """Notifica al administrador sobre un canje realizado."""
        from config.settings import settings # Importar aquí para evitar circular imports
        admin_message = (
            f"🔔 **¡Nuevo Canje de Recompensa!**\n"
            f"👤 Usuario: `{user.id}` (@{user.username or user.first_name})\n"
            f"🎁 Recompensa Canjeada: **{reward.name}** (ID: {reward.id})\n"
            f"💰 Puntos Gastados: {reward.cost_points}\n"
            f"📦 Stock Restante: {reward.stock if reward.stock != -1 else 'Ilimitado'}\n"
            f"💬 Contacta a este usuario para coordinar la entrega de la recompensa."
        )
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, admin_message, parse_mode="Markdown")
                logger.info(f"Notificación de canje enviada a admin {admin_id}.")
            except Exception as e:
                logger.error(f"No se pudo enviar notificación de canje a admin {admin_id}: {e}", exc_info=True)