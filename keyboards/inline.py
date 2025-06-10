# keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models.reward import Reward
from typing import List

def get_reaction_keyboard(post_id: str) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline para reacciones a una publicación.
    El post_id se usa para asegurar que un usuario solo reaccione una vez por publicación.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔥 Me encantó (+5 Puntos)", callback_data=f"react_post:{post_id}:5"),
        InlineKeyboardButton(text="❤️ Me fascinó (+5 Puntos)", callback_data=f"react_post:{post_id}:5")
    )
    # Podemos añadir más reacciones o incluso un botón para 'ver mi progreso' si es necesario
    return builder.as_markup()

def get_survey_options_keyboard(survey_id: str, options: list[str]) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline para opciones de encuesta.
    Cada opción tendrá un callback_data que incluye el survey_id y la opción elegida.
    """
    builder = InlineKeyboardBuilder()
    for i, option_text in enumerate(options):
        # Asignamos 5 puntos por participación en encuestas
        builder.row(InlineKeyboardButton(text=option_text, callback_data=f"survey_vote:{survey_id}:{i}:5"))
    return builder.as_markup()

def get_narrative_decision_keyboard(decision_id: str, options: dict[str, str]) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline para decisiones narrativas, otorgando puntos.
    options: {"Botón A": "callback_value_A", "Botón B": "callback_value_B"}
    """
    builder = InlineKeyboardBuilder()
    for text, value in options.items():
        # Asignamos 10 puntos por participar en decisiones narrativas
        builder.row(InlineKeyboardButton(text=text, callback_data=f"narrative_choice:{decision_id}:{value}:10"))
    return builder.as_markup()

def get_rewards_catalog_keyboard(rewards: List[Reward]) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline para navegar por el catálogo de recompensas.
    """
    builder = InlineKeyboardBuilder()
    for reward in rewards:
        builder.row(
            InlineKeyboardButton(text=f"{reward.name} ({reward.cost_points} Pts)", callback_data=f"show_reward:{reward.id}")
        )
    return builder.as_markup()

def get_confirm_redeem_keyboard(reward_id: int) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline para confirmar el canje de una recompensa.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Confirmar Canje", callback_data=f"redeem_confirm:{reward_id}"),
        InlineKeyboardButton(text="❌ Cancelar", callback_data="redeem_cancel")
    )
    return builder.as_markup()