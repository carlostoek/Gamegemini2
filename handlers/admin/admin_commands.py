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
            "Uso incorrecto. Formato: `/sumarpuntos [ID_usuario] [monto_MXN] [Descripción Opcional]`\n"
            "Ej: `/sumarpuntos 123456789 350.00 Acceso Canal VIP`"
        )
        return

    user_id_str, amount_str, _, description_str = match.groups()
    target_user_id = int(user_id_str)
    amount_mxn = float(amount_str)
    description = description_str.strip() if description_str else None

    logger.info(f"Admin {message.from_user.id} intentando sumar {amount_mxn} MXN a usuario {target_user_id} por '{description or 'N/A'}'.")

    purchase_service = PurchaseService(session)
    updated_user, points_awarded = await purchase_service.register_purchase(target_user_id, amount_mxn, description)

    if updated_user:
        response_message = (
            f"✅ Se han sumado **{points_awarded} puntos** por una compra de **{amount_mxn} MXN** "
            f"al usuario `{target_user_id}` (ahora tiene {updated_user.points} puntos, Nivel: {updated_user.level})."
        )
        if description:
            response_message += f"\nDescripción: _{description}_"
        await message.reply(response_message, parse_mode="Markdown")
    else:
        await message.reply(
            f"❌ Error: No se pudo registrar la compra para el usuario `{target_user_id}`. "
            "Asegúrate de que el ID de usuario sea correcto y que el usuario haya interactuado antes con el bot."
        )