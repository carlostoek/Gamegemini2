# database/models/level.py
from sqlalchemy import Column, Integer, String, Text
from database.db import Base

class Level(Base):
    """
    Modelo para los niveles de gamificación.
    Define los rangos de puntos y el nombre del nivel.
    """
    __tablename__ = 'levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, comment="Nombre del nivel (e.g., Suscriptor Íntimo)")
    min_points = Column(Integer, unique=True, nullable=False, comment="Puntos mínimos para alcanzar este nivel")
    max_points = Column(Integer, nullable=True, comment="Puntos máximos para este nivel (None si es el último nivel)")
    benefits = Column(Text, nullable=True, comment="Descripción de los beneficios de este nivel")

    def __repr__(self):
        return f"<Level(name='{self.name}', min_points={self.min_points}, max_points={self.max_points})>"

# Datos iniciales para los niveles. Se insertarán si la tabla está vacía.
INITIAL_LEVELS = [
    {"name": "Suscriptor Íntimo", "min_points": 0, "max_points": 99, "benefits": "Acceso completo al canal VIP. Insignia digital: 'Nuevo Suscriptor Íntimo'."},
    {"name": "Conocedor Apasionado", "min_points": 100, "max_points": 499, "benefits": "Contenido extra exclusivo (ej. imágenes o videos adicionales, previews)."},
    {"name": "Maestro del Deseo", "min_points": 500, "max_points": 999, "benefits": "Sorteos exclusivos, acceso a contenido “detrás de cámaras”."},
    {"name": "Leyenda VIP", "min_points": 1000, "max_points": 1999, "benefits": "Acceso anticipado a lanzamientos de contenido o eventos especiales."},
    {"name": "Ícono VIP", "min_points": 2000, "max_points": 3499, "benefits": "Contenido personalizado (ej. dedicatoria en video, si es viable)."},
    {"name": "Leyenda Suprema", "min_points": 3500, "max_points": None, "benefits": "Invitación a un evento virtual privado con la creadora (ej. Q&A exclusivo)."}
]