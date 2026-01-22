"""
Servicio de generación de CSS para fuentes.
Genera dinámicamente el fonts.css con @font-face para cada variante.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from app.config.settings import get_settings
from app.services.brand_service import BrandService, get_brand_service


class FontService:
    """Servicio para generar CSS de fuentes."""

    def __init__(self, brand_service: Optional[BrandService] = None):
        self._settings = get_settings()
        self._brand_service = brand_service or get_brand_service()
        self._css_cache: Dict[str, str] = {}

    def _get_font_format(self, filename: str) -> str:
        """
        Determina el formato de fuente basado en la extensión.

        Args:
            filename: Nombre del archivo de fuente

        Returns:
            Formato para usar en CSS (woff2, woff, truetype, opentype)
        """
        extension = filename.lower().split(".")[-1]
        formats = {
            "woff2": "woff2",
            "woff": "woff",
            "ttf": "truetype",
            "otf": "opentype",
            "eot": "embedded-opentype"
        }
        return formats.get(extension, "truetype")

    def _generate_font_face(
        self,
        family_name: str,
        src_url: str,
        weight: int,
        style: str
    ) -> str:
        """
        Genera una regla @font-face.

        Args:
            family_name: Nombre de la familia de fuentes
            src_url: URL pública del archivo de fuente
            weight: Peso de la fuente (300, 400, 700, etc.)
            style: Estilo de la fuente (normal, italic)

        Returns:
            Bloque CSS @font-face
        """
        font_format = self._get_font_format(src_url)

        return f"""@font-face {{
  font-family: '{family_name}';
  src: url('{src_url}') format('{font_format}');
  font-weight: {weight};
  font-style: {style};
  font-display: swap;
}}"""

    def generate_fonts_css(self, brand_id: str) -> str:
        """
        Genera el CSS completo con todas las fuentes del brand.

        Args:
            brand_id: Identificador del brand

        Returns:
            CSS completo con todas las @font-face

        Raises:
            BrandNotFoundError: Si el brand no existe
        """
        # Verificar cache
        cache_key = brand_id.lower()
        if self._settings.ENABLE_CACHE and cache_key in self._css_cache:
            return self._css_cache[cache_key]

        brand_config = self._brand_service.get_brand_config(brand_id)
        fonts_config = brand_config.get("fonts", {})

        css_blocks = []
        css_blocks.append(f"/* Fonts for {brand_config['customerName']} */")
        css_blocks.append(f"/* Generated dynamically - DO NOT EDIT */\n")

        # Procesar fuente primaria
        if "primary" in fonts_config:
            primary = fonts_config["primary"]
            primary_with_urls = self._brand_service.build_font_urls(brand_id, primary)
            css_blocks.append(f"/* Primary Font: {primary['name']} */")

            for variant in primary_with_urls["variants"]:
                css_blocks.append(
                    self._generate_font_face(
                        family_name=primary["name"],
                        src_url=variant["src"],
                        weight=variant["weight"],
                        style=variant["style"]
                    )
                )

        # Procesar fuente secundaria
        if "secondary" in fonts_config and fonts_config["secondary"]:
            secondary = fonts_config["secondary"]
            secondary_with_urls = self._brand_service.build_font_urls(brand_id, secondary)
            css_blocks.append(f"\n/* Secondary Font: {secondary['name']} */")

            for variant in secondary_with_urls["variants"]:
                css_blocks.append(
                    self._generate_font_face(
                        family_name=secondary["name"],
                        src_url=variant["src"],
                        weight=variant["weight"],
                        style=variant["style"]
                    )
                )

        # Variables CSS de conveniencia
        fallback = fonts_config.get("fallback", "Arial, sans-serif")
        primary_name = fonts_config.get("primary", {}).get("name", "Arial")
        secondary_name = fonts_config.get("secondary", {}).get("name", primary_name)

        css_blocks.append(f"""
/* CSS Custom Properties */
:root {{
  --font-primary: '{primary_name}', {fallback};
  --font-secondary: '{secondary_name}', {fallback};
  --font-fallback: {fallback};
}}""")

        css_content = "\n\n".join(css_blocks)

        # Guardar en cache
        if self._settings.ENABLE_CACHE:
            self._css_cache[cache_key] = css_content

        return css_content

    def clear_cache(self, brand_id: Optional[str] = None) -> None:
        """
        Limpia el cache de CSS.

        Args:
            brand_id: Si se especifica, solo limpia el cache de ese brand.
                     Si es None, limpia todo el cache.
        """
        if brand_id:
            cache_key = brand_id.lower()
            if cache_key in self._css_cache:
                del self._css_cache[cache_key]
        else:
            self._css_cache.clear()


@lru_cache()
def get_font_service() -> FontService:
    """Obtiene una instancia cacheada del servicio."""
    return FontService()
