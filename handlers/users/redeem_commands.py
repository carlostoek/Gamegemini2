# handlers/users/redeem_commands.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.reward_service import RewardService
from utils.formatter import format_reward_details
from keyboards.inline import get_rewards_catalog_keyboard, get_confirm_redeem_keyboard
from utils.logger import logger

router = Router()

@router.message(F.text == "/catalogo")
async def cmd_catalog(message: Message, db_user: User, session: AsyncSession):
    """
    Handler para el comando /catalogo.
    Muestra la lista de recompensas disponibles para canjear.
    """
    logger.info(f"Usuario {db_user.id} ({db_user.username}) usó /catalogo.")

    reward_service = RewardService(session, message.bot) # Pasamos el objeto bot para las notificaciones
    rewards = await reward_service.get_active_rewards()

    if not rewards:
        await message.reply("El Catálogo VIP está vacío por el momento. ¡Vuelve pronto para nuevas recompensas!")
        return

    catalog_message = "🎁 **Catálogo VIP de Recompensas** 🎁\n\n"
    for reward in rewards:
        catalog_message += f"**ID:** `{reward.id}` | {reward.name} - `{reward.cost_points}` Pts\n"
        catalog_message += f"  _Descripción:_ {reward.description}\n"
        catalog_message += f"  _Stock:_ {'Ilimitado' if reward.stock == -1 else reward.stock}\n\n"

    # También podemos usar el teclado inline para mostrar las opciones directamente
    # y mejorar la experiencia de usuario
    keyboard = get_rewards_catalog_keyboard(rewards)

    await message.reply(
        "Aquí están las recompensas disponibles para canjear. ¡Haz clic en una para ver más detalles o usar `/canjear [ID]` para canjearla!\n\n" + catalog_message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("show_reward:"))
async def handle_show_reward_callback(callback_query: CallbackQuery, db_user: User, session: AsyncSession):
    """
    Maneja el callback para mostrar detalles de una recompensa específica.
    """
    reward_id = int(callback_query.data.split(':')[1])
    logger.info(f"Usuario {db_user.id} solicitó ver detalles de recompensa ID {reward_id}.")

    reward_service = RewardService(session, callback_query.bot)
    reward = await reward_service.get_reward_by_id(reward_id)

    if not reward:
        await callback_query.answer("La recompensa no fue encontrada.", show_alert=True)
        return

    details_message = format_reward_details(reward)
    confirm_keyboard = get_confirm_redeem_keyboard(reward.id)

    await callback_query.message.edit_text(
        f"✨ **Detalles de la Recompensa** ✨\n\n{details_message}\n\n¿Deseas canjear esta recompensa?",
        reply_markup=confirm_keyboard,
        parse_mode="Markdown"
    )
    await callback_query.answer() # Descartar el "cargando" del botón

@router.callback_query(F.data.startswith("redeem_confirm:"))
async def handle_redeem_confirm_callback(callback_query: CallbackQuery, db_user: User, session: AsyncSession):
    """
    Maneja el callback de confirmación de canje.
    """
    reward_id = int(callback_query.data.split(':')[1])
    logger.info(f"Usuario {db_user.id} confirmó canje de recompensa ID {reward_id}.")

    reward_service = RewardService(session, callback_query.bot)
    success, message = await reward_service.redeem_reward(db_user, reward_id)

    # Actualizar el mensaje original con el resultado del canje
    if success:
        await callback_query.message.edit_text(
            f"🎉 ¡Canje realizado!\n\n{message}",
            reply_markup=None, # Remover botones para evitar re-canjes
            parse_mode="Markdown"
        )
    else:
        await callback_query.message.edit_text(
            f"❌ No se pudo canjear la recompensa.\n\n{message}",
            reply_markup=get_confirm_redeem_keyboard(reward_id), # Mantener botones si falló por puntos/stock
            parse_mode="Markdown"
        )
    await callback_query.answer(message, show_alert=True)


@router.callback_query(F.data == "redeem_cancel")
async def handle_redeem_cancel_callback(callback_query: CallbackQuery, db_user: User):
    """
    Maneja el callback para cancelar el canje.
    """
    logger.info(f"Usuario {db_user.id} canceló el canje de recompensa.")
    await callback_query.message.edit_text("Canje cancelado. Puedes volver a ver el catálogo con `/catalogo`.")
    await callback_query.answer("Canje cancelado.")

@router.message(F.text.regexp(r"^/canjear (\d+)$"))
async def cmd_redeem(message: Message, db_user: User, session: AsyncSession):
    """
    Handler para el comando /canjear [ID_recompensa].
    Permite al usuario iniciar el canje directamente por ID.
    """
    match = re.match(r"^/canjear (\d+)$", message.text)
    if not match:
        await message.reply(
            "Uso incorrecto. Formato: `/canjear [ID_recompensa]`\n"
            "Ej: `/canjear 1`"
        )
        return

    reward_id = int(match.group(1))
    logger.info(f"Usuario {db_user.id} intentó canjear recompensa ID {reward_id} vía comando.")

    reward_service = RewardService(session, message.bot)
    reward = await reward_service.get_reward_by_id(reward_id)

    if not reward or not reward.is_active:
        await message.reply("❌ La recompensa que intentas canjear no existe o no está activa.")
        return
    
    if reward.stock != -1 and reward.stock <= 0:
        await message.reply(f"❌ Lo siento, la recompensa '{reward.name}' está agotada.")
        return

    # Presentar la opción de confirmación al usuario
    details_message = format_reward_details(reward)
    confirm_keyboard = get_confirm_redeem_keyboard(reward.id)

    await message.reply(
        f"✨ **Detalles de la Recompensa** ✨\n\n{details_message}\n\n¿Deseas confirmar el canje de esta recompensa?",
        reply_markup=confirm_keyboard,
        parse_mode="Markdown"
    )