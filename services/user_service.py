# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from database.models.user import User
from utils.logger import logger

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        """Obtiene un usuario por su ID."""
        result = await self.session.execute(select(User).filter_by(id=user_id))
        return result.scalars().first()

    async def create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
        """Crea un nuevo usuario en la base de datos."""
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            join_date=datetime.now(),
            last_daily_reset=datetime.now()
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Usuario creado: {user_id} ({username})")
        return user

    async def update_user_points(self, user: User, points_to_add: int) -> User:
        """Actualiza los puntos de un usuario y recalcula su nivel."""
        user.points += points_to_add
        if user.points < 0: # Asegurarse de que los puntos no sean negativos
            user.points = 0
        
        # El nivel se recalcula en LevelService, solo necesitamos actualizar el campo
        from services.level_service import LevelService
        level_service = LevelService(self.session)
        user.level = await level_service.get_user_level(user.points)
        
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Puntos de usuario {user.id} actualizados: {user.points} (Nivel: {user.level})")
        return user

    async def update_user_interaction_data(self, user: User, points_gained_today: int) -> User:
        """
        Actualiza los datos de interacción diaria del usuario.
        Resetea el contador diario si ha pasado un día.
        """
        now = datetime.now()
        if user.last_daily_reset.date() < now.date():
            user.daily_points_earned = 0
            user.last_daily_reset = now
            logger.info(f"Reseteo de puntos diarios para usuario {user.id}.")

        user.daily_points_earned += points_gained_today
        user.last_interaction_date = now
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def increment_purchases_count(self, user: User) -> User:
        """Incrementa el contador de compras del usuario."""
        user.purchases_count += 1
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Contador de compras de usuario {user.id} incrementado a {user.purchases_count}.")
        return user