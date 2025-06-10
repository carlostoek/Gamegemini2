# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
from pydantic import Field # Solo Field, ya no necesitamos validator si ADMIN_IDS se maneja como list[int] JSON

# Cargar variables de entorno desde .env si existe (útil para desarrollo local)
load_dotenv()

class Settings(BaseSettings):
    """
    Clase para gestionar la configuración del bot, cargando variables de entorno.
    """
    # Configuración de Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore' # Ignorar variables no definidas en la clase
    )

    BOT_TOKEN: str
    DATABASE_URL: str # ¡Esperamos una única DATABASE_URL!
    ADMIN_IDS: list[int] = Field(default_factory=list) # Esperamos una lista de enteros, con default_factory para una lista vacía

    # Eliminamos el método __pydantic_init__ o el validador,
    # ya que Pydantic-settings con list[int] espera JSON array directamente.
    # Si la variable de entorno de Railway es '[123456789]', Pydantic lo parseará directamente.


# Crear una instancia de Settings que se usará en toda la aplicación
settings = Settings()
