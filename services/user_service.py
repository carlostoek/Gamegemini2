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
            join_date=datetime.now()
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Usuario creado: {user_id} ({username})")
        return user

    async def update_user_points(self, user: User, points_to_add: int) -> User:
        """Actualiza los puntos de un usuario y recalcula su nivel."""
        user.points += points_to_add
        if user.points < 0:  # Asegurarse de que los puntos no sean negativos
            user.points = 0
        
        # Recalcular nivel basado en puntos
        from services.level_service import LevelService
        level_service = LevelService(self.session)
        user.level_id = await level_service.get_user_level(user.points)
        
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Puntos de usuario {user.id} actualizados: {user.points} (Nivel ID: {user.level_id})")
        return user

    async def update_user_interaction_data(self, user: User, points_gained_today: int) -> User:
        """
        Actualiza los datos de interacción del usuario.
        """
        now = datetime.now()
        user.last_interaction_at = now
        user.interactions_count += 1
        
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def increment_purchases_count(self, user: User) -> User:
        """Incrementa el contador de compras del usuario."""
        user.purchase_count += 1
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Contador de compras de usuario {user.id} incrementado a {user.purchase_count}.")
        return user