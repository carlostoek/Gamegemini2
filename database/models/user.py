# el_juego_del_divan/database/models/user.py
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Text, DateTime
from sqlalchemy.sql import func
from database.base_model import Base # Importa Base desde base_model.py

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    points = Column(Integer, default=0)
    level_id = Column(Integer, default=1) # ID del nivel actual del usuario
    badges_json = Column(Text, default="[]") # Almacena un JSON de insignias
    is_admin = Column(Boolean, default=False)
    # Campos para seguimiento de interacción y permanencia
    join_date = Column(DateTime(timezone=True), default=func.now())
    last_interaction_at = Column(DateTime(timezone=True), default=func.now())
    interactions_count = Column(Integer, default=0) # Contador de interacciones diarias/periodo
    last_daily_reset = Column(DateTime(timezone=True), default=func.now()) # Para el reseteo diario de interacciones/puntos
    last_daily_points_claim = Column(DateTime(timezone=True), nullable=True) # Para control de puntos diarios

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', first_name='{self.first_name}')>"
