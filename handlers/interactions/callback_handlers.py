# handlers/interactions/callback_handlers.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.interaction_service import InteractionService
from utils.logger import logger

router = Router()

@router.callback_query(F.data.startswith("react_post:"))
async def handle_reaction_callback(callback_query: CallbackQuery, db_user: User, session: AsyncSession):
    """
    Maneja las reacciones a publicaciones desde botones inline.
    Formato de callback_data: "react_post:<post_id>:<points>"
    """
    _, post_id, points_str = callback_query.data.split(':')
    points = int(points_str)

    logger.info(f"Usuario {db_user.id} reaccionó al post {post_id} con {points} puntos.")

    interaction_service = InteractionService(session)
    success, message = await interaction_service.process_reaction(db_user, post_id, points)

    await callback_query.answer(message, show_alert=False) # Muestra un pop-up discreto
    # Opcional: editar el mensaje original para indicar que ya reaccionó
    # if success:
    #     await callback_query.message.edit_reply_markup(reply_markup=None) # Remueve los botones una vez reaccionado


@router.callback_query(F.data.startswith("survey_vote:"))
async def handle_survey_callback(callback_query: CallbackQuery, db_user: User, session: AsyncSession):
    """
    Maneja los votos en encuestas desde botones inline.
    Formato de callback_data: "survey_vote:<survey_id>:<option_index>:<points>"
    """
    _, survey_id, option_index_str, points_str = callback_query.data.split(':')
    option_index = int(option_index_str)
    points = int(points_str)

    logger.info(f"Usuario {db_user.id} votó en encuesta {survey_id}, opción {option_index} con {points} puntos.")

    interaction_service = InteractionService(session)
    success, message = await interaction_service.process_survey_vote(db_user, survey_id, option_index, points)

    await callback_query.answer(message, show_alert=False)
    # Una vez votado, se podría deshabilitar el teclado o editar el mensaje para mostrar el resultado
    # await callback_query.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("narrative_choice:"))
async def handle_narrative_callback(callback_query: CallbackQuery, db_user: User, session: AsyncSession):
    """
    Maneja las decisiones narrativas desde botones inline.
    Formato de callback_data: "narrative_choice:<decision_id>:<choice_value>:<points>"
    """
    _, decision_id, choice_value, points_str = callback_query.data.split(':')
    points = int(points_str)

    logger.info(f"Usuario {db_user.id} eligió '{choice_value}' en narrativa {decision_id} con {points} puntos.")

    interaction_service = InteractionService(session)
    success, message = await interaction_service.process_narrative_choice(db_user, decision_id, choice_value, points)

    await callback_query.answer(message, show_alert=False)
    # await callback_query.message.edit_reply_markup(reply_markup=None)