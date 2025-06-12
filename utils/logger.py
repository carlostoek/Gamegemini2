# utils/logger.py
from loguru import logger
import sys

# Remover el handler por defecto de loguru para configurar el nuestro
logger.remove()

# Configurar el logger para escribir en stdout con formato y nivel de debug
logger.add(
    sys.stdout,
    level="INFO", # Cambiar a "DEBUG" para desarrollo, "INFO" para producción
    format="{time} {level} {message}",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Puedes añadir más sinks si necesitas escribir en un archivo:
# logger.add("file_{time}.log", rotation="1 day", retention="7 days", level="DEBUG")
