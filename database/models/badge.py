# el_juego_del_divan/database/models/badge.py
from sqlalchemy import Column, Integer, String, Text
from database.base_model import Base # Importa Base desde base_model.py

class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True) # <-- CORREGIDO: nullable=True
    image_url = Column(String, nullable=True) # <-- CORREGIDO: nullable=True

    def __repr__(self):
        return f"<Badge(id={self.id}, name='{self.name}')>"

# Datos iniciales para la tabla de insignias (si los usas)
INITIAL_BADGES = [
    {"id": 1, "name": "Nuevo Suscriptor Íntimo", "description": "Obtenida al unirte por primera vez.", "image_url": "✨"},
    {"id": 2, "name": "Charlatán Tempranero", "description": "Por interactuar a primera hora del día.", "image_url": "🗣️"},
    {"id": 3, "name": "Constante del Conocimiento", "description": "Por mantener una racha de interacciones diarias.", "image_url": "🧠"},
    {"id": 4, "name": "Comprador Compulsivo", "description": "Por canjear muchas recompensas.", "image_url": "🛍️"}
]
