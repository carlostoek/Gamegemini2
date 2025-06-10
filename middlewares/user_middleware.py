# middlewares/user_middleware.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.user import User
from utils.logger import logger
from database.models.badge import INITIAL_BADGES
from config.settings import Settings
import json # <--- Asegúrate de que json esté importado aquí

class UserMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        telegram_user = event.from_user
        if not telegram_user:
            return await handler(event, data)

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
                points=0,
                level_id=1,
                is_admin=telegram_user.id in self.settings.ADMIN_IDS
            )

            # Asignar la insignia "Nuevo Suscriptor Íntimo"
            new_user_badge = next((badge for badge in INITIAL_BADGES if badge['id'] == 1), None)
            if new_user_badge:
                # Si el usuario es nuevo, badges_json debería ser "[]", pero lo aseguramos
                badges = json.loads(new_user.badges_json if new_user.badges_json else "[]") # <--- ¡CAMBIO AQUÍ!
                if new_user_badge['name'] not in [b['name'] for b in badges]:
                    badges.append({"id": new_user_badge['id'], "name": new_user_badge['name'], "description": new_user_badge['description']})
                    new_user.badges_json = json.dumps(badges)
                    logger.info(f"Usuario {new_user.id} recibió la insignia '{new_user_badge['name']}'.")

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            user = new_user
            logger.info(f"Nuevo usuario registrado: {user.username or user.first_name} (ID: {user.id})")
        else:
            # Si el usuario ya existe, asegurar que badges_json no sea None al leerlo
            # CAMBIO AQUÍ: Asegurar que badges_json sea una cadena válida antes de cargarla
            user.badges_json = user.badges_json if user.badges_json is not None else "[]"
            # No necesitamos cargarla aquí, solo asegurarnos de que tenga un valor por defecto si es None
            # El código de arriba ya maneja la asignación de la insignia si el usuario es nuevo.
            # Aquí podríamos querer actualizar 'last_interaction_at' e 'interactions_count'
            user.last_interaction_at = func.now()
            user.interactions_count += 1
            await session.commit() # ¡Importante guardar los cambios!

        data["user"] = user

        return await handler(event, data)
