from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ...database import get_session
from ...services.user_service import UserService

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Profile", callback_data="profile"),
                InlineKeyboardButton(text="Help", callback_data="help"),
                InlineKeyboardButton(text="Level", callback_data="level"),
            ]
        ]
    )
    async with get_session() as session:
        service = UserService(session)
        await service.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            join_date=message.date,
        )
    await message.answer(
        f"Welcome {message.from_user.full_name}!",
        reply_markup=keyboard,
    )

