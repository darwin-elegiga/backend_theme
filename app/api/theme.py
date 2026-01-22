"""
Endpoints de la API de temas.
Proporciona el tema completo para el frontend.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models.theme_response import (
    ThemeResponse,
    ThemeData,
    Colors,
    Fonts,
    FontFamily,
    FontVariant,
    Logos,
    Placeholders,
    CarPlaceholders,
    MotoPlaceholders,
    OdometerPlaceholders,
    DocumentationPlaceholders,
    ErrorResponse
)
from app.services.brand_service import (
    BrandService,
    BrandNotFoundError,
    get_brand_service
)
from app.services.font_service import FontService, get_font_service


router = APIRouter(prefix="/api", tags=["theme"])


@router.get(
    "/theme/{brand_id}",
    response_model=ThemeResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Brand not found"}
    },
    summary="Obtiene el tema completo de un brand",
    description="""
    Retorna la configuración completa del tema para un brand específico,
    incluyendo colores, fuentes, logos y placeholders con URLs públicas
    listas para consumir.
    """
)
async def get_theme(brand_id: str) -> ThemeResponse:
    """
    Obtiene el tema completo de un brand.

    Args:
        brand_id: Identificador único del brand (ej: mapfre, santander)

    Returns:
        ThemeResponse con toda la configuración del tema

    Raises:
        HTTPException 404: Si el brand no existe
    """
    brand_service = get_brand_service()
    font_service = get_font_service()

    try:
        config = brand_service.get_brand_config(brand_id)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Brand not found",
                "detail": f"The brand '{brand_id}' does not exist. "
                         f"Available brands: {', '.join(brand_service.get_brand_ids())}"
            }
        )

    # Construir URLs para logos
    logos_urls = brand_service.build_logo_urls(brand_id, config["logos"])

    # Construir URLs para placeholders
    placeholders_urls = brand_service.build_placeholder_urls(
        brand_id,
        config["placeholders"]
    )

    # Construir configuración de fuentes con URLs
    fonts_config = config["fonts"]
    primary_font = brand_service.build_font_urls(brand_id, fonts_config["primary"])

    secondary_font = None
    if fonts_config.get("secondary"):
        secondary_font = brand_service.build_font_urls(brand_id, fonts_config["secondary"])

    # Construir respuesta
    theme_data = ThemeData(
        customerName=config["customerName"],
        colors=Colors(**config["colors"]),
        fonts=Fonts(
            primary=FontFamily(
                name=primary_font["name"],
                variants=[FontVariant(**v) for v in primary_font["variants"]]
            ),
            secondary=FontFamily(
                name=secondary_font["name"],
                variants=[FontVariant(**v) for v in secondary_font["variants"]]
            ) if secondary_font else None,
            fallback=fonts_config.get("fallback", "Arial, sans-serif"),
            cssUrl=brand_service.get_fonts_css_url(brand_id)
        ),
        logos=Logos(**logos_urls),
        placeholders=Placeholders(
            car=CarPlaceholders(**placeholders_urls["car"]),
            moto=MotoPlaceholders(**placeholders_urls["moto"]),
            odometer=OdometerPlaceholders(**placeholders_urls["odometer"]),
            documentation=DocumentationPlaceholders(**placeholders_urls["documentation"])
        )
    )

    return ThemeResponse(success=True, data=theme_data)


@router.get(
    "/fonts/{brand_id}/fonts.css",
    response_class=Response,
    summary="CSS de fuentes generado dinámicamente",
    description="""
    Genera dinámicamente el archivo CSS con las reglas @font-face
    para todas las fuentes del brand especificado.
    """
)
async def get_fonts_css(brand_id: str) -> Response:
    """
    Genera el CSS de fuentes para un brand.

    Args:
        brand_id: Identificador único del brand

    Returns:
        Response con el CSS de fuentes

    Raises:
        HTTPException 404: Si el brand no existe
    """
    brand_service = get_brand_service()
    font_service = get_font_service()

    try:
        css_content = font_service.generate_fonts_css(brand_id)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Brand not found",
                "detail": f"The brand '{brand_id}' does not exist. "
                         f"Available brands: {', '.join(brand_service.get_brand_ids())}"
            }
        )

    return Response(
        content=css_content,
        media_type="text/css",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f"inline; filename=fonts-{brand_id}.css"
        }
    )


@router.get(
    "/brands",
    summary="Lista los brands disponibles",
    description="Retorna la lista de identificadores de brands configurados."
)
async def list_brands() -> dict:
    """Lista todos los brands disponibles."""
    brand_service = get_brand_service()
    return {
        "success": True,
        "brands": brand_service.get_brand_ids()
    }


@router.get(
    "/health",
    summary="Health check",
    description="Endpoint para verificar que el servicio está activo."
)
async def health_check() -> dict:
    """Health check del servicio."""
    return {"status": "healthy", "service": "theme-api"}
