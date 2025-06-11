# database/models/user.py
from sqlalchemy import BigInteger, Column, String, Integer, DateTime, Boolean, DECIMAL
from sqlalchemy.sql import func
from database.base_model import Base # ¡Importación corregida!

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True) # ID de Telegram del usuario
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    points = Column(Integer, default=0)
    level_id = Column(Integer, default=1) # Por defecto al Nivel 1
    last_interaction_at = Column(DateTime, default=func.now())
    interactions_count = Column(Integer, default=0) # Contador de interacciones diarias
    last_daily_points_claim = Column(DateTime, nullable=True) # Ultima vez que reclamó puntos diarios (permanencia)
    is_admin = Column(Boolean, default=False)
    purchase_count = Column(Integer, default=0) # Contador de compras para bonus
    join_date = Column(DateTime, default=func.now()) # Fecha de unión para hitos de permanencia
    total_redeemed_rewards_value = Column(DECIMAL(10, 2), default=0.00) # Valor total de recompensas canjeadas
    badges_json = Column(String, default="[]") # Guardará una lista JSON de insignias ganadas

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', points={self.points})>"
