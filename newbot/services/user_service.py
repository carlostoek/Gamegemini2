from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, username: str | None = None) -> User:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            return user
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.commit()
        return user

    async def add_points(self, user: User, points: int):
        user.points += points
        await self.session.commit()

    async def top_users(self, limit: int = 10):
        result = await self.session.execute(select(User).order_by(User.points.desc()).limit(limit))
        return result.scalars().all()
