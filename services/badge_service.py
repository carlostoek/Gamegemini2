# services/badge_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from database.models.badge import Badge
from utils.logger import logger

class BadgeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_badge_by_id(self, badge_id: str) -> Badge | None:
        """Obtiene una insignia por su ID."""
        result = await self.session.execute(select(Badge).filter_by(id=badge_id))
        return result.scalars().first()

    async def award_badge(self, user: User, badge_id: str, badge_name: str = None) -> bool:
        """
        Otorga una insignia a un usuario si aún no la tiene.
        :param user: Objeto User al que se le otorgará la insignia.
        :param badge_id: El ID único de la insignia a otorgar.
        :param badge_name: El nombre visible de la insignia (opcional, para logging).
        :return: True si la insignia fue otorgada, False si ya la tenía.
        """
        if badge_id in user.badges:
            logger.debug(f"Usuario {user.id} ya tiene la insignia '{badge_id}'.")
            return False

        user.badges.append(badge_id)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Insignia '{badge_name or badge_id}' otorgada a usuario {user.id}. Insignias actuales: {user.badges}")
        return True
    
    async def get_user_badges(self, user: User) -> list[Badge]:
        """
        Obtiene una lista de objetos Badge que el usuario ha desbloqueado.
        """
        if not user.badges:
            return []
        
        result = await self.session.execute(
            select(Badge).filter(Badge.id.in_(user.badges))
        )
        return result.scalars().all()

    async def get_all_badges(self) -> list[Badge]:
        """
        Obtiene todas las insignias disponibles en el sistema.
        """
        result = await self.session.execute(select(Badge))
        return result.scalars().all()