# utils/decorators.py
from functools import wraps
from typing import Callable, Any, Awaitable

from aiogram import types
from aiogram.fsm.context import FSMContext

from config.settings import settings
from utils.logger import logger

def is_admin(func: Callable[[types.Message, FSMContext], Awaitable[Any]]) -> Callable[[types.Message, FSMContext], Awaitable[Any]]:
    """
    Decorador para verificar si el usuario que ejecuta el comando es un administrador.
    Requiere que `settings.ADMIN_IDS` esté configurado.
    """
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs) -> Any:
        if message.from_user.id in settings.ADMIN_IDS:
            return await func(message, *args, **kwargs)
        else:
            logger.warning(f"Intento de acceso no autorizado por usuario {message.from_user.id} a comando admin.")
            await message.reply("🚫 No tienes permisos para ejecutar este comando.")
    return wrapper