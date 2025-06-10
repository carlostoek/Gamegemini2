# database/models/purchase.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.base_model import Base # ¡Importación corregida!

class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    amount = Column(DECIMAL(10, 2), nullable=False) # Monto de la compra
    points_awarded = Column(Integer, nullable=False) # Puntos otorgados por esta compra
    description = Column(String, nullable=True)
    purchase_date = Column(DateTime, default=func.now())

    user = relationship("User") # Relación con el modelo User

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, amount={self.amount}, points={self.points_awarded})>"
