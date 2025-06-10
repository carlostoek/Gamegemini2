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
            .join(Level, User.level == Level.id)
            .order_by(desc(User.points))
            .limit(limit)
        )
        return result.all()

    async def get_user_rank(self, user_id: int) -> Optional[int]:
        """
        Obtiene la posición de un usuario específico en el ranking.
        """
        # Consulta para obtener los puntos de todos los usuarios
        # y luego determinar la posición del usuario en cuestión.
        # Esto puede ser ineficiente para muchos usuarios; una alternativa es una columna de rank precalculada
        # o un rank basado en un índice b-tree para un rendimiento óptimo.
        all_users_points = await self.session.execute(
            select(User.id, User.points)
            .order_by(desc(User.points))
        )
        ranked_users = [u[0] for u in all_users_points.all()] # Solo IDs ordenados por puntos

        try:
            return ranked_users.index(user_id) + 1
        except ValueError:
            return None # Usuario no encontrado en el ranking (ej. si no tiene puntos o es nuevo)