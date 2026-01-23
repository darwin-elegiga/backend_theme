"""
Servicio de mapeo de códigos URL a brands.
Por ahora usa un JSON estático, pero está diseñado para
migrar fácilmente a una consulta a un backend externo.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Optional

from app.config.settings import get_settings


class CodeNotFoundError(Exception):
    """Excepción cuando el código no existe."""
    pass


class CodeService:
    """Servicio para mapear códigos URL a brand IDs."""

    def __init__(self):
        self._settings = get_settings()
        self._codes_cache: Optional[Dict[str, str]] = None
        self._codes_file = os.path.join(
            os.path.dirname(self._settings.BRANDS_CONFIG_PATH),
            "brand_codes.json"
        )

    def _load_codes(self) -> Dict[str, str]:
        """
        Carga el mapeo de códigos desde JSON.

        En el futuro, este método puede ser reemplazado por una
        llamada HTTP a un backend externo.
        """
        if self._codes_cache is not None and self._settings.ENABLE_CACHE:
            return self._codes_cache

        with open(self._codes_file, "r", encoding="utf-8") as f:
            self._codes_cache = json.load(f)

        return self._codes_cache

    def get_brand_id_by_code(self, code: str) -> str:
        """
        Obtiene el brand ID correspondiente a un código URL.

        Args:
            code: Código URL (ej: "b911a374a2cb41")

        Returns:
            Brand ID (ej: "santander")

        Raises:
            CodeNotFoundError: Si el código no existe
        """
        codes = self._load_codes()

        if code not in codes:
            raise CodeNotFoundError(f"Code '{code}' not found")

        return codes[code]

    def code_exists(self, code: str) -> bool:
        """Verifica si un código existe."""
        codes = self._load_codes()
        return code in codes

    # === FUTURO: Método para consultar backend externo ===
    # async def get_brand_id_by_code_remote(self, code: str) -> str:
    #     """
    #     Obtiene el brand ID desde un backend externo.
    #
    #     Args:
    #         code: Código URL
    #
    #     Returns:
    #         Brand ID
    #     """
    #     import httpx
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(f"{BACKEND_URL}/api/codes/{code}")
    #         response.raise_for_status()
    #         data = response.json()
    #         return data["brand_id"]


@lru_cache()
def get_code_service() -> CodeService:
    """Obtiene una instancia cacheada del servicio."""
    return CodeService()
