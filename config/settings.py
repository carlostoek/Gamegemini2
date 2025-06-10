# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Clase para gestionar la configuración del bot, cargando variables de entorno.
    """
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    BOT_TOKEN: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    ADMIN_IDS: List[int] = [] # Se cargará como string y se convertirá a lista en main.py

    @classmethod
    def from_env(cls):
        """
        Carga la configuración desde el archivo .env.
        """
        return cls()

settings = Settings.from_env()

# Ajuste para ADMIN_IDS ya que pydantic-settings los carga como string.
# Esto se manejará en main.py o donde se necesite usar ADMIN_IDS.