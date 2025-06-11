# database/models/badge.py
from sqlalchemy import Column, Integer, String
from database.base_model import Base # ¡Importación corregida!

class Badge(Base):
    __tablename__ = 'badges'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(String, nullable=True) # URL de una imagen o emoji para la insignia

    def __repr__(self):
        return f"<Badge(id={self.id}, name='{self.name}')>"

# Datos iniciales para las insignias
INITIAL_BADGES = [
    {"id": 1, "name": "Nuevo Suscriptor Íntimo", "description": "Has dado el primer paso en la comunidad.", "image_url": "⭐"},
    {"id": 2, "name": "Primer Canje", "description": "¡Has canjeado tu primera recompensa!", "image_url": "🏅"},
    {"id": 3, "name": "Veterano Íntimo (6 meses)", "description": "Por 6 meses de permanencia continua.", "image_url": "🕰️"},
    {"id": 4, "name": "Maestro Antiguo (1 año)", "description": "Por un año de permanencia continua.", "image_url": "👑"},
    {"id": 5, "name": "Comprador Frecuente", "description": "Por realizar 5 o más compras en el canal.", "image_url": "🛍️"},
    {"id": 6, "name": "Reaccionador Activo", "description": "Por tus valiosas reacciones en el canal.", "image_url": "👍"},
    # Puedes añadir más insignias aquí
]
