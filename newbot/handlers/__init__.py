from aiogram import Router
from .commands import router as commands_router
from .user.start import router as start_router

router = Router()
router.include_router(commands_router)
router.include_router(start_router)

__all__ = ["router"]
