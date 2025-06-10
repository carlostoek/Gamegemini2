# middlewares/register_user.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from database.db import get_db
from database.models.user import User
from utils.logger import logger

class RegisterUserMiddleware(BaseMiddleware):
    """
    Middleware para registrar al usuario en la base de datos si no existe.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        username = event.from_user.username
        first_name = event.from_user.first_name
        last_name = event.from_user.last_name

        async for session in get_db(): # Obtener una sesión de DB
            user = await session.execute(select(User).filter_by(id=user_id))
            db_user = user.scalars().first()

            if not db_user:
                db_user = User(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    join_date=datetime.now(),
                    last_daily_reset=datetime.now() # Inicializa el reseteo diario
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                logger.info(f"Nuevo usuario registrado: {user_id} ({username})")
            else:
                # Actualizar username y first_name si han cambiado (opcional)
                if db_user.username != username:
                    db_user.username = username
                    await session.commit()
                if db_user.first_name != first_name:
                    db_user.first_name = first_name
                    await session.commit()
                # logger.debug(f"Usuario existente: {user_id} ({username})")

            # Añadir el objeto usuario de la base de datos a los datos que se pasan al handler
            data["db_user"] = db_user
            data["session"] = session # Pasamos la sesión para que los handlers puedan usarla directamente

            return await handler(event, data)