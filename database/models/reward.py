# database/models/reward.py
from sqlalchemy import Column, Integer, String, DECIMAL
from database.base_model import Base # ¡Importación corregida!

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    points_cost = Column(Integer, nullable=False)
    stock = Column(Integer, default=-1) # -1 para stock ilimitado, >0 para stock limitado
    image_url = Column(String, nullable=True) # URL de una imagen o emoji para la recompensa

    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', cost={self.points_cost}, stock={self.stock})>"

# Datos iniciales para las recompensas (Catálogo VIP)
INITIAL_REWARDS = [
    {"id": 1, "name": "Acceso VIP a Contenido Exclusivo", "description": "Acceso a una sección especial de nuestro canal con contenido premium.", "points_cost": 1000, "stock": -1, "image_url": "💎"},
    {"id": 2, "name": "Mención Especial en Directo", "description": "Tu nombre o usuario mencionado en nuestro próximo directo.", "points_cost": 500, "stock": 5, "image_url": "🎤"},
    {"id": 3, "name": "Sticker Personalizado del Canal", "description": "Un sticker digital único diseñado para ti.", "points_cost": 750, "stock": 10, "image_url": "🎨"},
    {"id": 4, "name": "Rol Especial en Discord (si aplica)", "description": "Un rol exclusivo en nuestro servidor de Discord.", "points_cost": 2000, "stock": -1, "image_url": "🛡️"},
    {"id": 5, "name": "Acceso Anticipado a Lanzamientos", "description": "Sé de los primeros en ver o probar nuestros próximos proyectos.", "points_cost": 1500, "stock": -1, "image_url": "🚀"},
    # Puedes añadir más recompensas aquí
]
