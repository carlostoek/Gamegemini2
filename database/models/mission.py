# el_juego_del_divan/database/models/mission.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from database.base_model import Base # Importa Base desde base_model.py

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    points_reward = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime(timezone=True), default=func.now())
    ends_at = Column(DateTime(timezone=True), nullable=True)
    # Tipo de misión (ej. 'interact_daily', 'join_event', 'reach_level')
    mission_type = Column(String, nullable=False)
    # Criterios adicionales en JSON (ej. {'target_count': 5} para 'interact_daily')
    criteria_json = Column(Text, default="{}")

    def __repr__(self):
        return f"<Mission(id={self.id}, name='{self.name}', type='{self.mission_type}')>"
