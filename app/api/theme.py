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
    BrandNotFoundError,
    get_brand_service
)
from app.services.font_service import get_font_service
from app.services.code_service import get_code_service


router = APIRouter(prefix="/api", tags=["theme"])


async def resolve_to_brand_id(code_or_brand: str) -> str:
    """
    Resuelve un código URL o brand_id a un brand_id válido.

    Primero intenta resolver como código URL.
    Si no existe, lo trata como brand_id directo.

    Args:
        code_or_brand: Código URL o brand_id

    Returns:
        brand_id resuelto

    Raises:
        BrandNotFoundError: Si no existe ni como código ni como brand
    """
    code_service = get_code_service()
    brand_service = get_brand_service()

    # Primero intentar como código URL
    if await code_service.code_exists(code_or_brand):
        return await code_service.get_brand_id_by_code(code_or_brand)

    # Si no es código, verificar si es un brand_id válido
    if brand_service.brand_exists(code_or_brand):
        return code_or_brand.lower()

    # No existe ni como código ni como brand
    raise BrandNotFoundError(f"'{code_or_brand}' not found as code or brand")


@router.get(
    "/theme/{url_code}",
    response_model=ThemeResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Code/Brand not found"}
    },
    summary="Obtiene el tema completo",
    description="""
    Retorna la configuración completa del tema.
    Acepta un código URL (ej: b911a374a2cb41) o un brand_id directo (ej: mapfre).
    """
)
async def get_theme(url_code: str) -> ThemeResponse:
    """
    Obtiene el tema completo.

    Args:
        url_code: Código URL o brand_id

    Returns:
        ThemeResponse con toda la configuración del tema
    """
    brand_service = get_brand_service()

    # Resolver código/brand a brand_id
    try:
        brand_id = await resolve_to_brand_id(url_code)
        config = brand_service.get_brand_config(brand_id)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Not found",
                "detail": f"'{url_code}' is not a valid code or brand. "
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
    "/theme/{url_code}/colors",
    summary="Obtiene solo los colores",
    description="Retorna únicamente la paleta de colores del tema."
)
async def get_theme_colors(url_code: str) -> dict:
    """
    Obtiene solo los colores.

    Args:
        url_code: Código URL o brand_id

    Returns:
        Diccionario con los colores del tema
    """
    brand_service = get_brand_service()

    try:
        brand_id = await resolve_to_brand_id(url_code)
        config = brand_service.get_brand_config(brand_id)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Not found",
                "detail": f"'{url_code}' is not a valid code or brand. "
                         f"Available brands: {', '.join(brand_service.get_brand_ids())}"
            }
        )

    return {
        "success": True,
        "customerName": config["customerName"],
        "colors": config["colors"]
    }


@router.get(
    "/fonts/{url_code}/fonts.css",
    response_class=Response,
    summary="CSS de fuentes generado dinámicamente",
    description="Genera el CSS con las reglas @font-face para las fuentes del brand."
)
async def get_fonts_css(url_code: str) -> Response:
    """
    Genera el CSS de fuentes.

    Args:
        url_code: Código URL o brand_id

    Returns:
        Response con el CSS de fuentes
    """
    brand_service = get_brand_service()
    font_service = get_font_service()

    try:
        brand_id = await resolve_to_brand_id(url_code)
        css_content = font_service.generate_fonts_css(brand_id)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Not found",
                "detail": f"'{url_code}' is not a valid code or brand."
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
