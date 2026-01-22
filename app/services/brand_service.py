"""
Servicio de gestión de marcas (brands).
Carga la configuración de brands.json y construye las URLs públicas.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.config.settings import get_settings


class BrandNotFoundError(Exception):
    """Excepción cuando el brand no existe."""
    pass


class BrandService:
    """Servicio para gestionar la configuración de marcas."""

    def __init__(self):
        self._settings = get_settings()
        self._brands_cache: Optional[Dict[str, Any]] = None

    def _load_brands(self) -> Dict[str, Any]:
        """Carga el archivo brands.json."""
        if self._brands_cache is not None and self._settings.ENABLE_CACHE:
            return self._brands_cache

        with open(self._settings.BRANDS_CONFIG_PATH, "r", encoding="utf-8") as f:
            self._brands_cache = json.load(f)

        return self._brands_cache

    def get_brand_ids(self) -> List[str]:
        """Retorna la lista de brand IDs disponibles."""
        brands = self._load_brands()
        return list(brands.keys())

    def brand_exists(self, brand_id: str) -> bool:
        """Verifica si un brand existe."""
        brands = self._load_brands()
        return brand_id.lower() in brands

    def get_brand_config(self, brand_id: str) -> Dict[str, Any]:
        """
        Obtiene la configuración raw de un brand.

        Args:
            brand_id: Identificador del brand (ej: "mapfre", "santander")

        Returns:
            Diccionario con la configuración del brand

        Raises:
            BrandNotFoundError: Si el brand no existe
        """
        brands = self._load_brands()
        brand_key = brand_id.lower()

        if brand_key not in brands:
            raise BrandNotFoundError(f"Brand '{brand_id}' not found")

        return brands[brand_key]

    def _build_static_url(self, brand_id: str, *path_parts: str) -> str:
        """
        Construye una URL pública para un recurso estático.

        Args:
            brand_id: Identificador del brand
            *path_parts: Partes del path del recurso

        Returns:
            URL pública completa
        """
        base = self._settings.STATIC_BASE_URL.rstrip("/")
        path = "/".join(path_parts)
        return f"{base}/brands/{brand_id}/{path}"

    def build_logo_urls(self, brand_id: str, logos_config: Dict[str, str]) -> Dict[str, str]:
        """Construye las URLs públicas para los logos."""
        return {
            key: self._build_static_url(brand_id, "images", filename)
            for key, filename in logos_config.items()
        }

    def build_placeholder_urls(
        self,
        brand_id: str,
        placeholders_config: Dict[str, Dict[str, str]]
    ) -> Dict[str, Dict[str, str]]:
        """Construye las URLs públicas para los placeholders."""
        result = {}
        for category, items in placeholders_config.items():
            result[category] = {
                key: self._build_static_url(brand_id, "images", "placeholders", path)
                for key, path in items.items()
            }
        return result

    def build_font_urls(
        self,
        brand_id: str,
        font_family: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Construye las URLs públicas para las variantes de una familia de fuentes.

        Args:
            brand_id: Identificador del brand
            font_family: Configuración de la familia de fuentes

        Returns:
            Familia de fuentes con URLs públicas
        """
        result = {
            "name": font_family["name"],
            "variants": []
        }

        for variant in font_family["variants"]:
            result["variants"].append({
                "src": self._build_static_url(brand_id, "fonts", variant["file"]),
                "weight": variant["weight"],
                "style": variant["style"]
            })

        return result

    def get_fonts_css_url(self, brand_id: str) -> str:
        """Retorna la URL del CSS de fuentes generado dinámicamente."""
        base = self._settings.STATIC_BASE_URL.rstrip("/")
        # Usamos el endpoint de la API, no un archivo estático
        return f"{base.replace('/static', '')}/api/fonts/{brand_id}/fonts.css"


@lru_cache()
def get_brand_service() -> BrandService:
    """Obtiene una instancia cacheada del servicio."""
    return BrandService()
