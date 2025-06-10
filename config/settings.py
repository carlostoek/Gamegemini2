# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
from pydantic import Field

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
    # CAMBIO AQUÍ: Ahora DATABASE_URL apuntará a un archivo SQLite local
    # No la necesitamos como variable de entorno si el archivo es local y fijo
    DATABASE_URL: str = "sqlite+aiosqlite:///./database.db" # <--- ¡CAMBIO CLAVE!
    ADMIN_IDS: list[int] = Field(default_factory=list)

# Crear una instancia de Settings que se usará en toda la aplicación
settings = Settings()
