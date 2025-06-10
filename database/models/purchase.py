# database/models/purchase.py
from sqlalchemy import Column, Integer, BigInteger, DateTime, Float, String
from sqlalchemy.sql import func
from database.db import Base

class Purchase(Base):
    """
    Modelo para registrar las compras de los usuarios en el sistema.
    """
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True, nullable=False, comment="ID del usuario que realizó la compra")
    amount_mxn = Column(Float, nullable=False, comment="Monto de la compra en MXN")
    points_awarded = Column(Integer, nullable=False, comment="Puntos otorgados por esta compra")
    purchase_date = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="Fecha y hora de la compra")
    description = Column(String, nullable=True, comment="Descripción opcional de la compra (ej. 'Acceso Canal VIP')")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, amount_mxn={self.amount_mxn}, points={self.points_awarded})>"