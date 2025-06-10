# middlewares/register_user.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

# Importa async_session_maker directamente desde db.py
from database.db import async_session_maker # <--- ¡IMPORTANTE!

from database.models.user import User
from utils.logger import logger

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
        # Usa async_session_maker para manejar la sesión directamente
        # Esto asegura que la sesión se abre y cierra correctamente para cada evento.
        async with async_session_maker() as session:
            user_id = event.from_user.id
            username = event.from_user.username
            first_name = event.from_user.first_name
            last_name = event.from_user.last_name

            # Inyecta la sesión en 'data' para que los handlers puedan acceder a ella
            data["session"] = session

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
                # Solo commitea si hay cambios para evitar commits innecesarios
                changed = False
                if db_user.username != username:
                    db_user.username = username
                    changed = True
                if db_user.first_name != first_name:
                    db_user.first_name = first_name
                    changed = True
                if changed:
                    await session.commit()
                # logger.debug(f"Usuario existente: {user_id} ({username})")

            # Añadir el objeto usuario de la base de datos a los datos que se pasan al handler
            data["user"] = db_user # Asumo que tus handlers esperan 'user' como en cmd_status

            # Continuar con la ejecución del handler
            return await handler(event, data)
