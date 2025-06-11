# handlers/users/redeem_commands.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from services.reward_service import RewardService
from utils.formatter import format_reward_details
from keyboards.inline import get_rewards_catalog_keyboard, get_confirm_redeem_keyboard
from utils.logger import logger
import re

router = Router()

@router.message(F.text == "/catalogo")
async def cmd_catalog(message: Message, user: User, session: AsyncSession):
    """
    Handler para el comando /catalogo.
    Muestra la lista de recompensas disponibles para canjear.
    """
    logger.info(f"Usuario {user.id} ({user.username}) usó /catalogo.")

    try:
        reward_service = RewardService(session, message.bot)
        rewards = await reward_service.get_active_rewards()

        if not rewards:
            await message.reply("🎁 El Catálogo VIP está vacío por el momento. ¡Vuelve pronto para nuevas recompensas!")
            return

        catalog_message = "🎁 **Catálogo VIP de Recompensas** 🎁\n\n"
        for reward in rewards:
            stock_text = "Ilimitado" if reward.stock == -1 else str(reward.stock)
            catalog_message += (
                f"**{reward.id}.** {reward.name}\n"
                f"   💰 Costo: **{reward.points_cost} puntos**\n"
                f"   📦 Stock: {stock_text}\n"
                f"   📝 {reward.description}\n\n"
            )

        catalog_message += (
            f"💎 **Tus puntos actuales:** {user.points}\n\n"
            f"💡 Usa `/canjear [ID]` para canjear una recompensa\n"
            f"Ejemplo: `/canjear 1`"
        )

        # Usar teclado inline para mejor experiencia
        keyboard = get_rewards_catalog_keyboard(rewards)

        await message.reply(
            catalog_message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en /catalogo para usuario {user.id}: {e}", exc_info=True)
        await message.reply("❌ Ocurrió un error al cargar el catálogo. Por favor, intenta de nuevo más tarde.")

@router.callback_query(F.data.startswith("show_reward:"))
async def handle_show_reward_callback(callback_query: CallbackQuery, user: User, session: AsyncSession):
    """
    Maneja el callback para mostrar detalles de una recompensa específica.
    """
    try:
        reward_id = int(callback_query.data.split(':')[1])
        logger.info(f"Usuario {user.id} solicitó ver detalles de recompensa ID {reward_id}.")

        reward_service = RewardService(session, callback_query.bot)
        reward = await reward_service.get_reward_by_id(reward_id)

        if not reward:
            await callback_query.answer("La recompensa no fue encontrada.", show_alert=True)
            return

        details_message = format_reward_details(reward)
        confirm_keyboard = get_confirm_redeem_keyboard(reward.id)

        await callback_query.message.edit_text(
            f"✨ **Detalles de la Recompensa** ✨\n\n{details_message}\n\n"
            f"💎 **Tus puntos:** {user.points}\n\n"
            f"¿Deseas canjear esta recompensa?",
            reply_markup=confirm_keyboard,
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error en show_reward callback: {e}", exc_info=True)
        await callback_query.answer("Error al cargar los detalles.", show_alert=True)

@router.callback_query(F.data.startswith("redeem_confirm:"))
async def handle_redeem_confirm_callback(callback_query: CallbackQuery, user: User, session: AsyncSession):
    """
    Maneja el callback de confirmación de canje.
    """
    try:
        reward_id = int(callback_query.data.split(':')[1])
        logger.info(f"Usuario {user.id} confirmó canje de recompensa ID {reward_id}.")

        reward_service = RewardService(session, callback_query.bot)
        success, message = await reward_service.redeem_reward(user, reward_id)

        if success:
            await callback_query.message.edit_text(
                f"🎉 **¡Canje realizado!**\n\n{message}",
                reply_markup=None,
                parse_mode="Markdown"
            )
        else:
            await callback_query.message.edit_text(
                f"❌ **No se pudo canjear la recompensa**\n\n{message}",
                reply_markup=get_confirm_redeem_keyboard(reward_id),
                parse_mode="Markdown"
            )
        await callback_query.answer(message[:100], show_alert=True)
        
    except Exception as e:
        logger.error(f"Error en redeem_confirm callback: {e}", exc_info=True)
        await callback_query.answer("Error al procesar el canje.", show_alert=True)

@router.callback_query(F.data == "redeem_cancel")
async def handle_redeem_cancel_callback(callback_query: CallbackQuery, user: User):
    """
    Maneja el callback para cancelar el canje.
    """
    logger.info(f"Usuario {user.id} canceló el canje de recompensa.")
    await callback_query.message.edit_text(
        "❌ **Canje cancelado**\n\nPuedes volver a ver el catálogo con `/catalogo`."
    )
    await callback_query.answer("Canje cancelado.")

@router.message(F.text.regexp(r"^/canjear (\d+)$"))
async def cmd_redeem(message: Message, user: User, session: AsyncSession):
    """
    Handler para el comando /canjear [ID_recompensa].
    Permite al usuario iniciar el canje directamente por ID.
    """
    try:
        match = re.match(r"^/canjear (\d+)$", message.text)
        if not match:
            await message.reply(
                "❌ **Uso incorrecto**\n\n"
                "Formato: `/canjear [ID_recompensa]`\n"
                "Ejemplo: `/canjear 1`\n\n"
                "Usa `/catalogo` para ver las recompensas disponibles."
            )
            return

        reward_id = int(match.group(1))
        logger.info(f"Usuario {user.id} intentó canjear recompensa ID {reward_id} vía comando.")

        reward_service = RewardService(session, message.bot)
        reward = await reward_service.get_reward_by_id(reward_id)

        if not reward:
            await message.reply("❌ La recompensa que intentas canjear no existe.")
            return
        
        if reward.stock != -1 and reward.stock <= 0:
            await message.reply(f"❌ Lo siento, la recompensa '{reward.name}' está agotada.")
            return

        # Presentar la opción de confirmación al usuario
        details_message = format_reward_details(reward)
        confirm_keyboard = get_confirm_redeem_keyboard(reward.id)

        await message.reply(
            f"✨ **Detalles de la Recompensa** ✨\n\n{details_message}\n\n"
            f"💎 **Tus puntos:** {user.points}\n\n"
            f"¿Deseas confirmar el canje de esta recompensa?",
            reply_markup=confirm_keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en /canjear para usuario {user.id}: {e}", exc_info=True)
        await message.reply("❌ Ocurrió un error al procesar tu solicitud. Por favor, intenta de nuevo más tarde.")