# services/purchase_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from database.models.purchase import Purchase
from services.user_service import UserService
from services.points_service import PointsService
from utils.logger import logger

class PurchaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)
        self.points_service = PointsService(session)

    async def register_purchase(self, user_id: int, amount_mxn: float, description: str = None) -> tuple[User | None, int]:
        """
        Registra una compra para un usuario, asigna puntos y aplica bonificaciones.
        Retorna el objeto User actualizado y los puntos totales otorgados.
        """
        user = await self.user_service.get_user(user_id)
        if not user:
            logger.warning(f"Intento de registrar compra para usuario {user_id} no encontrado.")
            return None, 0

        points_awarded = self._calculate_points(amount_mxn)
        initial_points = points_awarded # Puntos base antes de bonificaciones

        # Bonificaciones por fidelidad en compras
        # Bonus por 5 compras: +150 puntos y contenido gratuito
        # Asumo que el "contenido gratuito" se entregará fuera del bot o se notificará
        if user.purchases_count % 5 == 4: # Si esta es la 5ta compra (0-indexed)
            points_awarded += 150
            logger.info(f"Bonus de 5 compras para usuario {user.id}. +150 puntos.")
            # TODO: Notificar al usuario sobre el contenido gratuito
            
        # Podríamos añadir lógica para renovación anticipada/automática aquí si el amount_mxn lo indica
        # Ejemplo: if description == "Renovación Canal VIP" and amount_mxn == 250:
        #            points_awarded = 160 # O si es anticipada, +50 puntos. Esto requeriría más lógica de estado.

        # Registra la compra en la base de datos
        purchase = Purchase(
            user_id=user_id,
            amount_mxn=amount_mxn,
            points_awarded=points_awarded,
            description=description
        )
        self.session.add(purchase)
        await self.session.commit()
        await self.session.refresh(purchase)

        # Actualiza los puntos y el contador de compras del usuario
        updated_user = await self.points_service.add_points(user, points_awarded, reason=f"Compra de {amount_mxn} MXN")
        updated_user = await self.user_service.increment_purchases_count(updated_user) # Incrementa el contador de compras

        logger.info(f"Compra de {amount_mxn} MXN registrada para usuario {user_id}. Puntos otorgados: {points_awarded}.")
        return updated_user, points_awarded

    def _calculate_points(self, amount_mxn: float) -> int:
        """
        Calcula los puntos a otorgar basados en el monto gastado.
        Según el informe de gamificación.
        """
        if amount_mxn >= 500:
            return 350
        elif amount_mxn >= 350:
            return 250 if amount_mxn == 350 else 200 # Distingue entre "Acceso Canal VIP" y "Contenido Especial (350)"
        elif amount_mxn >= 250:
            return 180 if amount_mxn == 250 else 150 # Distingue entre "Renovación Canal VIP"
        elif amount_mxn >= 150:
            return 100
        elif amount_mxn >= 100:
            return 70
        else:
            return int(amount_mxn * 0.5) # Un default para montos pequeños, ejemplo 50% del monto