# el_juego_del_divan/middlewares/register_user.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

# === CAMBIO APLICADO: Importación corregida sin el prefijo 'el_juego_del_divan' ===
from database.db import async_session_maker
from database.models.user import User
from utils.logger import logger
# ======================================================================================

class RegisterUserMiddleware(BaseMiddleware):
    """
    Middleware para registrar al usuario en la base de datos si no existe
    y para inyectar la sesión de DB y el objeto User en los handlers.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            user_id = event.from_user.id
            username = event.from_user.username
            first_name = event.from_user.first_name
            last_name = event.from_user.last_name

            data["session"] = session

            user_query = await session.execute(select(User).filter_by(id=user_id))
            db_user = user_query.scalars().first()

            if not db_user:
                db_user = User(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    join_date=datetime.now(),
                    last_daily_reset=datetime.now()
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                logger.info(f"Nuevo usuario registrado: {user_id} ({username})")
            else:
                changed = False
                if db_user.username != username:
                    db_user.username = username
                    changed = True
                if db_user.first_name != first_name:
                    db_user.first_name = first_name
                    changed = True
                if changed:
                    await session.commit()

            data["user"] = db_user

            return await handler(event, data)
