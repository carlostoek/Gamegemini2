# services/badge_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from database.models.badge import Badge
from utils.logger import logger
import json

class BadgeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_badge_by_id(self, badge_id: int) -> Badge | None:
        """Obtiene una insignia por su ID."""
        result = await self.session.execute(select(Badge).filter_by(id=badge_id))
        return result.scalars().first()

    async def award_badge(self, user: User, badge_id: int, badge_name: str = None) -> bool:
        """
        Otorga una insignia a un usuario si aún no la tiene.
        :param user: Objeto User al que se le otorgará la insignia.
        :param badge_id: El ID único de la insignia a otorgar.
        :param badge_name: El nombre visible de la insignia (opcional, para logging).
        :return: True si la insignia fue otorgada, False si ya la tenía.
        """
        try:
            # Cargar insignias actuales del usuario
            current_badges = json.loads(user.badges_json if user.badges_json else "[]")
            
            # Verificar si ya tiene la insignia
            if any(badge['id'] == badge_id for badge in current_badges):
                logger.debug(f"Usuario {user.id} ya tiene la insignia con ID '{badge_id}'.")
                return False

            # Obtener información completa de la insignia
            badge = await self.get_badge_by_id(badge_id)
            if not badge:
                logger.error(f"Insignia con ID {badge_id} no encontrada.")
                return False

            # Añadir la nueva insignia
            new_badge = {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "image_url": badge.image_url
            }
            current_badges.append(new_badge)
            
            # Actualizar el usuario
            user.badges_json = json.dumps(current_badges)
            await self.session.commit()
            await self.session.refresh(user)
            
            logger.info(f"Insignia '{badge.name}' otorgada a usuario {user.id}.")
            return True
            
        except Exception as e:
            logger.error(f"Error al otorgar insignia {badge_id} a usuario {user.id}: {e}", exc_info=True)
            return False
    
    async def get_user_badges(self, user: User) -> list[dict]:
        """
        Obtiene una lista de insignias que el usuario ha desbloqueado.
        """
        try:
            badges_data = json.loads(user.badges_json if user.badges_json else "[]")
            return badges_data
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar insignias para usuario {user.id}")
            return []

    async def get_all_badges(self) -> list[Badge]:
        """
        Obtiene todas las insignias disponibles en el sistema.
        """
        result = await self.session.execute(select(Badge))
        return result.scalars().all()