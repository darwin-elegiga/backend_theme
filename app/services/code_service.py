"""
Servicio de mapeo de códigos URL a brands.
Consulta el endpoint externo de verificaciones para obtener
el customerName (brand) asociado a cada urlCode.
"""
from __future__ import annotations

import httpx
from functools import lru_cache
from typing import Dict, Optional

from app.config.settings import get_settings


class CodeNotFoundError(Exception):
    """Excepción cuando el código no existe."""
    pass


class CodeServiceError(Exception):
    """Excepción cuando hay un error al consultar el servicio externo."""
    pass


class CodeService:
    """Servicio para mapear códigos URL a brand IDs."""

    def __init__(self):
        self._settings = get_settings()
        self._codes_cache: Dict[str, str] = {}
        self._verification_api_url = "https://api.vda.es.int.emea.aws.mapfre.com/verifications"

    async def get_brand_id_by_code(self, code: str) -> str:
        """
        Obtiene el brand ID correspondiente a un código URL.
        Consulta el endpoint externo y extrae el customerName.

        Args:
            code: Código URL (ej: "b911a374a2cb41")

        Returns:
            Brand ID extraído del campo customerName (ej: "Mapfre")

        Raises:
            CodeNotFoundError: Si el código no existe o no se encuentra
            CodeServiceError: Si hay un error al consultar el servicio
        """
        # Verificar cache si está habilitado
        if self._settings.ENABLE_CACHE and code in self._codes_cache:
            return self._codes_cache[code]

        # Consultar el endpoint externo
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self._verification_api_url}/{code}"
                print(f"Requesting brand for code '{code}' at URL: {url}")
                
                response = await client.get(url)
                
                print(f"Received response for code '{code}':")
                print(f"  URL: {response.url}")
                print(f"  Status Code: {response.status_code}")
                print(f"  Response Body: {response.text}")

                if response.status_code == 404:
                    raise CodeNotFoundError(f"Code '{code}' not found")
                
                response.raise_for_status()
                data = response.json()
                
                # Extraer el customerName del response
                customer_name = data.get("customerName")
                
                if not customer_name:
                    raise CodeServiceError(
                        f"Response for code '{code}' does not contain 'customerName' field"
                    )
                
                # Guardar en cache
                if self._settings.ENABLE_CACHE:
                    self._codes_cache[code] = customer_name
                
                return customer_name
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise CodeNotFoundError(f"Code '{code}' not found")
            raise CodeServiceError(
                f"Error querying verification API for code '{code}': {e}"
            )
        except httpx.RequestError as e:
            raise CodeServiceError(
                f"Network error while querying verification API: {e}"
            )
        except Exception as e:
            raise CodeServiceError(
                f"Unexpected error while getting brand for code '{code}': {e}"
            )

    async def code_exists(self, code: str) -> bool:
        """
        Verifica si un código existe consultando el endpoint externo.
        
        Args:
            code: Código URL
            
        Returns:
            True si el código existe, False en caso contrario
        """
        try:
            await self.get_brand_id_by_code(code)
            return True
        except CodeNotFoundError:
            return False
        except CodeServiceError:
            # En caso de error del servicio, asumimos que no existe
            return False

    def clear_cache(self) -> None:
        """Limpia el cache de códigos."""
        self._codes_cache.clear()


@lru_cache()
def get_code_service() -> CodeService:
    """Obtiene una instancia cacheada del servicio."""
    return CodeService()