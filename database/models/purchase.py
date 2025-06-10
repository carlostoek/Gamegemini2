# el_juego_del_divan/database/models/purchase.py
from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.base_model import Base # Importa Base desde base_model.py

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    purchase_date = Column(DateTime(timezone=True), default=func.now())
    points_spent = Column(Integer, nullable=False)

    # Relaciones para acceder a los objetos User y Reward
    user = relationship("User")
    reward = relationship("Reward")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, reward_id={self.reward_id}, points_spent={self.points_spent})>"
