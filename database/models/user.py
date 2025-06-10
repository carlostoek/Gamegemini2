# database/models/user.py
from sqlalchemy import Column, BigInteger, Integer, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from database.db import Base
import datetime

class User(Base):
    """
    Modelo de usuario para el sistema de gamificación.
    Almacena puntos, nivel, fecha de ingreso, insignias, etc.
    """
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, unique=True, index=True, comment="Telegram User ID")
    username = Column(String, nullable=True, comment="Telegram Username")
    first_name = Column(String, nullable=True, comment="Telegram First Name")
    last_name = Column(String, nullable=True, comment="Telegram Last Name")

    # Datos de gamificación
    points = Column(Integer, default=0, nullable=False, comment="Puntos de gamificación acumulados")
    level = Column(Integer, default=0, nullable=False, comment="Nivel actual del usuario")
    join_date = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="Fecha de ingreso al canal/bot")
    last_interaction_date = Column(DateTime(timezone=True), nullable=True, comment="Última fecha de interacción (reacción/encuesta)")
    daily_points_earned = Column(Integer, default=0, nullable=False, comment="Puntos ganados hoy por interacciones")
    last_daily_reset = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="Fecha del último reseteo de puntos diarios")

    # Para el sistema de permanencia
    last_permanence_check = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="Última vez que se otorgaron puntos por permanencia")
    weekly_streak = Column(Integer, default=0, nullable=False, comment="Racha semanal de permanencia")

    # Para el sistema de insignias (almacenamos los IDs de las insignias desbloqueadas)
    badges = Column(ARRAY(String), default=[], nullable=False, comment="Lista de IDs de insignias desbloqueadas")

    # Contador de compras para bonificaciones
    purchases_count = Column(Integer, default=0, nullable=False, comment="Número total de compras registradas")

    # Para misiones (podríamos usar otro modelo o una columna JSONB más adelante)
    # Por ahora, simplemente para demostrar la estructura
    completed_missions = Column(ARRAY(String), default=[], nullable=False, comment="Lista de IDs de misiones completadas")


    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', points={self.points}, level={self.level})>"