# database/models/reward.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from database.db import Base

class Reward(Base):
    """
    Modelo para las recompensas disponibles en el Catálogo VIP.
    """
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment="Nombre de la recompensa")
    description = Column(Text, nullable=False, comment="Descripción detallada de la recompensa")
    cost_points = Column(Integer, nullable=False, comment="Costo de la recompensa en puntos")
    stock = Column(Integer, default=-1, comment="Stock disponible (-1 para ilimitado)")
    is_active = Column(Boolean, default=True, comment="Indica si la recompensa está activa y disponible")
    type = Column(String, default="digital", comment="Tipo de recompensa (ej. 'digital', 'fisica', 'acceso', 'descuento')")
    image_url = Column(String, nullable=True, comment="URL opcional de una imagen de la recompensa")

    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', cost={self.cost_points}, stock={self.stock})>"

# Datos iniciales para algunas recompensas de ejemplo
INITIAL_REWARDS = [
    {
        "id": 1,
        "name": "Saludo Personalizado por Mensaje",
        "description": "Recibe un mensaje de voz o texto personalizado de la creadora de contenido.",
        "cost_points": 1000,
        "stock": -1, # Ilimitado
        "is_active": True,
        "type": "digital"
    },
    {
        "id": 2,
        "name": "Acceso a Contenido Exclusivo (1 Semana)",
        "description": "Acceso por una semana a un canal privado con contenido nunca antes visto.",
        "cost_points": 2500,
        "stock": -1,
        "is_active": True,
        "type": "acceso"
    },
    {
        "id": 3,
        "name": "Sesión de Preguntas y Respuestas (Q&A) Privada",
        "description": "Participa en una sesión de Q&A exclusiva con la creadora por videollamada (grupo reducido).",
        "cost_points": 5000,
        "stock": 5,
        "is_active": True,
        "type": "interaccion"
    },
    {
        "id": 4,
        "name": "Foto Autografiada Digital",
        "description": "Una foto digital exclusiva autografiada por la creadora, enviada directamente a tu DM.",
        "cost_points": 1500,
        "stock": -1,
        "is_active": True,
        "type": "digital"
    },
    {
        "id": 5,
        "name": "Descuento del 10% en Merchandising",
        "description": "Obtén un código de descuento para tu próxima compra en la tienda de merchandising oficial.",
        "cost_points": 800,
        "stock": -1,
        "is_active": True,
        "type": "descuento"
    },
    {
        "id": 6,
        "name": "Mensaje de Feliz Cumpleaños (Audio)",
        "description": "Recibe un mensaje de audio personalizado de Feliz Cumpleaños en tu día especial.",
        "cost_points": 700,
        "stock": -1,
        "is_active": True,
        "type": "digital"
    }
]