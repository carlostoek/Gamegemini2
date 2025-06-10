# services/points_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.user_service import UserService
from utils.logger import logger

class PointsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)

    async def add_points(self, user: User, points_to_add: int, reason: str = "Desconocida") -> User:
        """
        Añade puntos a un usuario y actualiza su nivel.
        """
        if points_to_add <= 0:
            logger.warning(f"Intento de añadir 0 o menos puntos a usuario {user.id}. Razón: {reason}")
            return user
        
        updated_user = await self.user_service.update_user_points(user, points_to_add)
        logger.info(f"Añadidos {points_to_add} puntos a usuario {user.id} por '{reason}'. Nuevos puntos: {updated_user.points}")
        return updated_user

    async def deduct_points(self, user: User, points_to_deduct: int, reason: str = "Desconocida") -> User:
        """
        Deduce puntos de un usuario y actualiza su nivel.
        Asegura que los puntos no sean negativos.
        """
        if points_to_deduct <= 0:
            logger.warning(f"Intento de deducir 0 o menos puntos a usuario {user.id}. Razón: {reason}")
            return user

        updated_user = await self.user_service.update_user_points(user, -points_to_deduct)
        logger.info(f"Deducidos {points_to_deduct} puntos de usuario {user.id} por '{reason}'. Nuevos puntos: {updated_user.points}")
        return updated_user