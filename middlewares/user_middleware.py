# middlewares/user_middleware.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from utils.logger import logger
from database.models.badge import INITIAL_BADGES # Para la insignia de "Nuevo Suscriptor"

class UserMiddleware(BaseMiddleware):
    """
    Middleware que asegura que cada mensaje y callback_query tenga un objeto User asociado.
    Crea el usuario si no existe y lo añade a los datos del evento.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        telegram_user = event.from_user
        if not telegram_user:
            return await handler(event, data) # No hay usuario de Telegram, pasar

        session: AsyncSession = data.get("session")
        if not session:
            logger.error("DbSessionMiddleware no se ejecutó antes que UserMiddleware.")
            return await handler(event, data)

        user = await session.execute(
            select(User).filter_by(id=telegram_user.id)
        )
        user = user.scalars().first()

        if not user:
            # Crear nuevo usuario
            new_user = User(
                id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                points=0, # Inicia con 0 puntos
                level_id=1, # Por defecto al nivel 1
                is_admin=telegram_user.id in data["settings"].ADMIN_IDS # Revisa si es admin
            )

            # Asignar la insignia "Nuevo Suscriptor Íntimo"
            new_user_badge = next((badge for badge in INITIAL_BADGES if badge['id'] == 1), None)
            if new_user_badge:
                # En una aplicación real, probablemente tendrías una tabla de relación
                # o un campo que guarde IDs de insignias. Por ahora, asumimos json
                import json # Importar json aquí para evitar conflictos si no se usa globalmente
                badges = json.loads(new_user.badges_json)
                if new_user_badge['name'] not in [b['name'] for b in badges]:
                    badges.append({"id": new_user_badge['id'], "name": new_user_badge['name'], "description": new_user_badge['description']})
                    new_user.badges_json = json.dumps(badges)
                    logger.info(f"Usuario {new_user.id} recibió la insignia '{new_user_badge['name']}'.")


            session.add(new_user)
            await session.commit()
            await session.refresh(new_user) # Asegurar que el objeto User esté actualizado
            user = new_user
            logger.info(f"Nuevo usuario registrado: {user.username or user.first_name} (ID: {user.id})")

        data["user"] = user # Añadir el objeto User a los datos del evento

        return await handler(event, data)
