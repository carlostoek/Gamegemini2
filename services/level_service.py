# services/level_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models.level import Level
from utils.logger import logger

class LevelService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_levels(self) -> list[Level]:
        """Obtiene todos los niveles definidos en la base de datos, ordenados por puntos."""
        result = await self.session.execute(select(Level).order_by(Level.points_required))
        return result.scalars().all()

    async def get_user_level(self, points: int) -> int:
        """
        Determina el nivel de un usuario basándose en sus puntos.
        Devuelve el ID del nivel.
        """
        levels = await self.get_all_levels()
        current_level_id = 1  # Nivel predeterminado

        for level in levels:
            if points >= level.points_required:
                current_level_id = level.id
            else:
                break  # Los niveles están ordenados, si no cumple se detiene

        return current_level_id
    
    async def get_level_by_id(self, level_id: int) -> Level | None:
        """Obtiene un objeto Level por su ID."""
        result = await self.session.execute(select(Level).filter_by(id=level_id))
        return result.scalars().first()
    
    async def get_level_by_name(self, name: str) -> Level | None:
        """Obtiene un objeto Level por su nombre."""
        result = await self.session.execute(select(Level).filter_by(name=name))
        return result.scalars().first()

    async def get_next_level_info(self, current_points: int) -> tuple[Level | None, int]:
        """
        Obtiene información sobre el siguiente nivel y los puntos restantes para alcanzarlo.
        Retorna (siguiente_nivel_obj, puntos_restantes).
        """
        levels = await self.get_all_levels()
        next_level = None
        points_to_next_level = 0

        for level in levels:
            if level.points_required > current_points:
                next_level = level
                points_to_next_level = level.points_required - current_points
                break

        return next_level, points_to_next_level