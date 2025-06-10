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
        result = await self.session.execute(select(Level).order_by(Level.min_points))
        return result.scalars().all()

    async def get_user_level(self, points: int) -> int:
        """
        Determina el nivel de un usuario basándose en sus puntos.
        Devuelve el ID del nivel.
        """
        levels = await self.get_all_levels()
        current_level_id = 0 # Nivel predeterminado (Suscriptor Íntimo)

        for level in levels:
            if level.min_points <= points:
                if level.max_points is None or points <= level.max_points:
                    current_level_id = level.id
                elif level.max_points is not None and points > level.max_points and level == levels[-1]:
                    # Si los puntos superan el máximo del último nivel, se quedan en el último nivel
                    current_level_id = level.id
            else:
                break # Los niveles están ordenados, si no cumple con min_points, no cumplirá con los siguientes

        if current_level_id == 0 and levels:
            # Si por alguna razón los puntos son menores que el min_points del primer nivel,
            # asegúrate de que esté en el primer nivel (id=1 si asumimos id start at 1)
            # O el nivel con min_points 0
            for level in levels:
                if level.min_points == 0:
                    current_level_id = level.id
                    break
            if current_level_id == 0: # Fallback si no hay nivel con 0 min_points
                current_level_id = levels[0].id # Asigna el primer nivel

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

        for i, level in enumerate(levels):
            if level.min_points > current_points:
                next_level = level
                points_to_next_level = level.min_points - current_points
                break
            elif i == len(levels) - 1: # Es el último nivel
                next_level = None # Ya está en el nivel más alto
                points_to_next_level = 0 # No hay siguiente nivel

        return next_level, points_to_next_level