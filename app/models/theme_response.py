"""
Modelos Pydantic para la respuesta del tema.
Define la estructura completa del JSON que consume el frontend.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel


class FontVariant(BaseModel):
    """Variante de una fuente con peso y estilo."""
    src: str
    weight: int
    style: str


class FontFamily(BaseModel):
    """Familia de fuentes con sus variantes."""
    name: str
    variants: List[FontVariant]


class Fonts(BaseModel):
    """Configuración completa de fuentes."""
    primary: FontFamily
    secondary: Optional[FontFamily] = None
    fallback: str = "Arial, sans-serif"
    cssUrl: str  # URL al CSS generado dinámicamente


class Colors(BaseModel):
    """Paleta de colores del tema."""
    primary: str
    primaryDisabled: str
    secondary: str
    link: str
    background: str
    backgroundSecondary: str
    headerBackground: str
    navBar: str
    navBarSecondary: str
    text: str
    textSecondary: str
    border: str
    overlay: str
    error: str
    errorBackground: str
    errorText: str
    success: str
    warning: str
    buttonNext: str
    buttonNextText: str
    buttonBack: str
    buttonBackText: str


class Logos(BaseModel):
    """URLs de logos del brand."""
    header: str
    favicon: str


# Placeholders dinámicos - permite cualquier estructura
CarPlaceholders = Dict[str, str]
MotoPlaceholders = Dict[str, str]
OdometerPlaceholders = Dict[str, str]
DocumentationPlaceholders = Dict[str, str]


class Placeholders(BaseModel):
    """Todos los placeholders organizados por categoría."""
    car: Dict[str, str]
    moto: Dict[str, str]
    odometer: Dict[str, str]
    documentation: Dict[str, str]


class ThemeData(BaseModel):
    """Datos completos del tema."""
    customerName: str
    colors: Colors
    fonts: Fonts
    logos: Logos
    placeholders: Placeholders


class ThemeResponse(BaseModel):
    """Respuesta completa del endpoint /theme/{brandId}."""
    success: bool
    data: ThemeData


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    success: bool = False
    error: str
    detail: Optional[str] = None
