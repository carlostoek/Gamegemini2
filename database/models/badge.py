# database/models/badge.py
from sqlalchemy import Column, Integer, String, Text
from database.db import Base

class Badge(Base):
    """
    Modelo para las insignias del sistema de gamificación.
    Define los logros que los usuarios pueden desbloquear.
    """
    __tablename__ = 'badges'

    id = Column(String, primary_key=True, unique=True, index=True, comment="ID único de la insignia (ej. 'veterano_intimo')")
    name = Column(String, nullable=False, comment="Nombre visible de la insignia")
    description = Column(Text, nullable=False, comment="Descripción de cómo se obtiene la insignia")
    icon = Column(String, nullable=True, comment="Emoji o URL a un ícono de la insignia")

    def __repr__(self):
        return f"<Badge(id='{self.id}', name='{self.name}')>"

# Datos iniciales para las insignias. Se insertarán si la tabla está vacía.
INITIAL_BADGES = [
    {"id": "nuevo_suscriptor_intimo", "name": "Nuevo Suscriptor Íntimo", "description": "Tu primera insignia al unirte al canal.", "icon": "🔰"},
    {"id": "veterano_intimo", "name": "Veterano Íntimo", "description": "Por permanecer 6+ meses en el canal.", "icon": "🕰️"},
    {"id": "big_spender_vip", "name": "Big Spender VIP", "description": "Por gastar $500+ MXN en contenido VIP.", "icon": "💸"},
    {"id": "fan_leal_apasionado", "name": "Fan Leal Apasionado", "description": "Por realizar 50+ reacciones o participaciones en encuestas.", "icon": "💖"},
    {"id": "racha_ardiente", "name": "Racha Ardiente", "description": "Por reaccionar durante 7 días seguidos.", "icon": "🔥"},
    {"id": "primer_canje", "name": "Primer Canje", "description": "Por realizar tu primer canje de puntos en el Catálogo VIP.", "icon": "🎁"},
    {"id": "cazador_tesoros", "name": "Cazador de Tesoros", "description": "Por encontrar un emoji o mensaje oculto en una publicación.", "icon": "🔍"}
]