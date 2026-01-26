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
    secondary: str
    link: str
    background: str
    backgroundSecondary: str
    headerBackground: str
    navBar: str
    navBarSecondary: str
    text: str
    textSecondary: str
    overlay: str
    error: str
    errorBackground: str
    errorText: str
    success: str
    warning: str
    buttonNext: str
    buttonNextDisabled: str
    buttonNextText: str
    buttonBack: str
    buttonBackDisabled: str
    buttonBackText: str
    skeleton: str


class Logos(BaseModel):
    """URLs de logos del brand."""
    header: str
    favicon: str


class CarPlaceholders(BaseModel):
    """Placeholders de vehículo (coche) - 8 ángulos."""
    front: str
    frontRight: str
    right: str
    rearRight: str
    rear: str
    rearLeft: str
    left: str
    frontLeft: str


class MotoPlaceholders(BaseModel):
    """Placeholders de moto - 4 ángulos."""
    front: str
    right: str
    rear: str
    left: str


class OdometerPlaceholders(BaseModel):
    """Placeholders de odómetro."""
    mileage: str


class DocumentationPlaceholders(BaseModel):
    """Placeholders de documentación."""
    dniFront: str
    dniBack: str
    licenseFront: str
    licenseBack: str
    dataSheetFront: str
    dataSheetBack: str
    circulationFront: str
    circulationBack: str


class Placeholders(BaseModel):
    """Todos los placeholders organizados por categoría."""
    car: CarPlaceholders
    moto: MotoPlaceholders
    odometer: OdometerPlaceholders
    documentation: DocumentationPlaceholders


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
