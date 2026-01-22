"""
Configuración centralizada del backend.
Permite migrar fácilmente de URLs locales a CDN.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # Base URL para assets estáticos
    # En desarrollo: URL del backend
    # En producción: URL del CDN
    STATIC_BASE_URL: str = os.getenv("STATIC_BASE_URL", "http://localhost:8000/static")

    # Ruta al archivo de configuración de brands
    BRANDS_CONFIG_PATH: str = os.getenv(
        "BRANDS_CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), "brands.json")
    )

    # Directorio de archivos estáticos
    STATIC_DIR: str = os.getenv(
        "STATIC_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
    )

    # Habilitar cache en memoria
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # TTL del cache en segundos (1 hora por defecto)
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada."""
    return Settings()
