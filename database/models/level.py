# database/models/level.py
from sqlalchemy import Column, Integer, String
from database.base_model import Base # ¡Importación corregida!

class Level(Base):
    __tablename__ = 'levels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    points_required = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Level(id={self.id}, name='{self.name}', points_required={self.points_required})>"

# Datos iniciales para los niveles de usuario
INITIAL_LEVELS = [
    {"id": 1, "name": "Novato Íntimo", "points_required": 0, "description": "Acabas de unirte a la comunidad."},
    {"id": 2, "name": "Curioso Íntimo", "points_required": 500, "description": "Explorando y aprendiendo más."},
    {"id": 3, "name": "Participante Íntimo", "points_required": 1500, "description": "Activo y comprometido."},
    {"id": 4, "name": "Experto Íntimo", "points_required": 3000, "description": "Conocedor y contribuidor."},
    {"id": 5, "name": "Maestro Íntimo", "points_required": 5000, "description": "Guía y referente de la comunidad."},
    # Puedes añadir más niveles aquí
]
