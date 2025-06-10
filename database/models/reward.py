# el_juego_del_divan/database/models/reward.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from database.base_model import Base # Importa Base desde base_model.py

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True) # <-- CORREGIDO: nullable=True
    points_cost = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True) # Si la recompensa está disponible para canjear

    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', points_cost={self.points_cost})>"

# Datos iniciales para las recompensas (si los usas)
INITIAL_REWARDS = [
    {"id": 1, "name": "Acceso Exclusivo a Chat Privado", "description": "Desbloquea el acceso a un chat especial con la comunidad más cercana.", "points_cost": 2000},
    {"id": 2, "name": "Mención Especial en Directo", "description": "Tu nombre mencionado y agradecido en el próximo directo.", "points_cost": 500},
    {"id": 3, "name": "Emoji Personalizado", "description": "Un emoji exclusivo para ti en el chat principal.", "points_cost": 1000},
    {"id": 4, "name": "Participación en Sesión Q&A", "description": "Una pregunta directa respondida en la siguiente sesión de preguntas y respuestas.", "points_cost": 750}
]
