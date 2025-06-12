from aiogram import Router, F
from aiogram.types import Message
from ..database import get_session
from ..services.user_service import UserService
from ..services.gamification_service import GamificationService
from ..config import config

router = Router()

@router.message(F.text.regexp(r"^/addpoints \d+ \d+$"))
async def add_points_cmd(message: Message):
    if message.from_user.id not in config.admin_ids:
        await message.answer("No autorizado")
        return
    _, uid, pts = message.text.split()
    uid = int(uid)
    pts = int(pts)
    async with get_session() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create(uid)
        await user_service.add_points(user, pts)
        user.level = GamificationService.calculate_level(user.points)
        await session.commit()
        await message.answer(f"Usuario {uid} ahora tiene {user.points} puntos (Nivel {user.level})")

@router.message(F.text == "/leaderboard")
async def leaderboard_cmd(message: Message):
    async with get_session() as session:
        user_service = UserService(session)
        users = await user_service.top_users()
    lines = [f"{idx+1}. {u.telegram_id} - {u.points} pts" for idx, u in enumerate(users)]
    await message.answer("\n".join(lines) or "Sin usuarios")
