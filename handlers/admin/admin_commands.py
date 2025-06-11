# handlers/admin/admin_commands.py
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from services.purchase_service import PurchaseService
from utils.decorators import is_admin
from utils.logger import logger
import re

router = Router()

@router.message(F.text.regexp(r"^/sumarpuntos (\d+) (\d+(\.\d+)?)(.*)?$"))
@is_admin
async def cmd_add_points_by_purchase(message: Message, session: AsyncSession):
    """
    Handler para el comando /sumarpuntos [user_id] [monto] [descripción_opcional].
    Permite al administrador registrar una compra y asignar puntos a un usuario.
    Ej: /sumarpuntos 123456789 350.00 Acceso Canal VIP
    """
    match = re.match(r"^/sumarpuntos (\d+) (\d+(\.\d+)?)(.*)?$", message.text)
    if not match:
        await message.reply(
            "❌ **Uso incorrecto**\n\n"
            "**Formato:** `/sumarpuntos [ID_usuario] [monto_MXN] [Descripción Opcional]`\n"
            "**Ejemplo:** `/sumarpuntos 123456789 350.00 Acceso Canal VIP`",
            parse_mode="Markdown"
        )
        return

    user_id_str, amount_str, _, description_str = match.groups()
    target_user_id = int(user_id_str)
    amount_mxn = float(amount_str)
    description = description_str.strip() if description_str else None

    logger.info(f"Admin {message.from_user.id} intentando sumar {amount_mxn} MXN a usuario {target_user_id} por '{description or 'N/A'}'.")

    try:
        purchase_service = PurchaseService(session)
        updated_user, points_awarded = await purchase_service.register_purchase(target_user_id, amount_mxn, description)

        if updated_user:
            response_message = (
                f"✅ **Compra registrada exitosamente**\n\n"
                f"👤 **Usuario:** `{target_user_id}`\n"
                f"💰 **Monto:** {amount_mxn} MXN\n"
                f"🎯 **Puntos otorgados:** {points_awarded}\n"
                f"💎 **Puntos totales del usuario:** {updated_user.points}\n"
                f"✨ **Nivel actual:** {updated_user.level_id}"
            )
            if description:
                response_message += f"\n📝 **Descripción:** _{description}_"
            
            await message.reply(response_message, parse_mode="Markdown")
        else:
            await message.reply(
                f"❌ **Error:** No se pudo registrar la compra para el usuario `{target_user_id}`.\n"
                "Asegúrate de que el ID de usuario sea correcto y que el usuario haya interactuado antes con el bot.",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error en comando /sumarpuntos: {e}", exc_info=True)
        await message.reply(
            "❌ Ocurrió un error al procesar la compra. Por favor, intenta de nuevo más tarde."
        )