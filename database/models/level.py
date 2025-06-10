# el_juego_del_divan/database/models/level.py
from sqlalchemy import Column, Integer, String
from database.base_model import Base # Importa Base desde base_model.py

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    points_required = Column(Integer, nullable=False, default=0)
    # Otros atributos si los tienes, como una descripción o un multiplicador de puntos

    def __repr__(self):
        return f"<Level(id={self.id}, name='{self.name}', points_required={self.points_required})>"

# Datos iniciales para la tabla de niveles (si los usas)
INITIAL_LEVELS = [
    {"id": 1, "name": "Novato", "points_required": 0},
    {"id": 2, "name": "Curioso", "points_required": 100},
    {"id": 3, "name": "Explorador", "points_required": 500},
    {"id": 4, "name": "Visionario", "points_required": 1500},
    {"id": 5, "name": "Maestro del Diván", "points_required": 5000}
]
