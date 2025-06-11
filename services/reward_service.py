# services/reward_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from database.models.reward import Reward
from services.points_service import PointsService
from services.badge_service import BadgeService
from utils.logger import logger
from typing import List, Optional
from aiogram import Bot
import json

class RewardService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.points_service = PointsService(session)
        self.badge_service = BadgeService(session)

    async def get_active_rewards(self) -> List[Reward]:
        """
        Obtiene todas las recompensas activas disponibles en el catálogo.
        """
        result = await self.session.execute(
            select(Reward).filter(Reward.stock != 0)  # Excluir las agotadas
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
        try:
            reward = await self.get_reward_by_id(reward_id)

            if not reward:
                return False, "❌ La recompensa que intentas canjear no existe."

            if reward.stock != -1 and reward.stock <= 0:
                return False, f"❌ Lo siento, la recompensa '{reward.name}' está agotada."

            if user.points < reward.points_cost:
                return False, (f"❌ No tienes suficientes puntos para canjear '{reward.name}'. "
                               f"Necesitas {reward.points_cost} puntos y solo tienes {user.points}.")

            # Procesar el canje
            # Restar puntos
            await self.points_service.deduct_points(user, reward.points_cost, f"Canje de recompensa: {reward.name}")
            
            # Disminuir stock si no es ilimitado
            if reward.stock != -1:
                reward.stock -= 1
                self.session.add(reward)

            # Otorgar insignia de primer canje si aplica
            user_badges = json.loads(user.badges_json if user.badges_json else "[]")
            if not any(badge['id'] == 2 for badge in user_badges):  # ID 2 = "Primer Canje"
                await self.badge_service.award_badge(user, 2, "Primer Canje")
                await self._send_notification_to_user(user.id, "🎉 ¡Felicidades! Has realizado tu primer canje y desbloqueado la insignia 'Primer Canje'.")

            await self.session.commit()
            await self.session.refresh(user)
            
            # Notificar al administrador
            await self._notify_admin_about_redemption(user, reward)

            message_to_user = (
                f"✅ **¡Canje exitoso!**\n\n"
                f"🎁 Has canjeado: **{reward.name}**\n"
                f"💰 Puntos gastados: **{reward.points_cost}**\n"
                f"💎 Puntos restantes: **{user.points}**\n\n"
                f"📞 Nos pondremos en contacto contigo pronto para coordinar la entrega de tu recompensa."
            )
            return True, message_to_user

        except Exception as e:
            await self.session.rollback()
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
        from config.settings import settings
        admin_message = (
            f"🔔 **¡Nuevo Canje de Recompensa!**\n\n"
            f"👤 **Usuario:** `{user.id}` (@{user.username or user.first_name})\n"
            f"🎁 **Recompensa:** {reward.name} (ID: {reward.id})\n"
            f"💰 **Puntos gastados:** {reward.points_cost}\n"
            f"📦 **Stock restante:** {reward.stock if reward.stock != -1 else 'Ilimitado'}\n\n"
            f"💬 Contacta a este usuario para coordinar la entrega de la recompensa."
        )
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, admin_message, parse_mode="Markdown")
                logger.info(f"Notificación de canje enviada a admin {admin_id}.")
            except Exception as e:
                logger.error(f"No se pudo enviar notificación de canje a admin {admin_id}: {e}", exc_info=True)