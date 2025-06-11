# services/ranking_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.user import User
from database.models.level import Level
from utils.logger import logger
from typing import List, Tuple, Optional

class RankingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_top_users(self, limit: int = 10) -> List[Tuple[User, Level]]:
        """
        Obtiene los usuarios con más puntos, junto con su nivel.
        """
        result = await self.session.execute(
            select(User, Level)
            .join(Level, User.level_id == Level.id)
            .order_by(desc(User.points))
            .limit(limit)
        )
        return result.all()

    async def get_user_rank(self, user_id: int) -> Optional[int]:
        """
        Obtiene la posición de un usuario específico en el ranking.
        """
        # Obtener todos los usuarios ordenados por puntos
        all_users_result = await self.session.execute(
            select(User.id)
            .order_by(desc(User.points))
        )
        ranked_user_ids = [user_id for (user_id,) in all_users_result.all()]

        try:
            return ranked_user_ids.index(user_id) + 1
        except ValueError:
            return None  # Usuario no encontrado