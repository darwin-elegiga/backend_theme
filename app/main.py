"""
Backend de Temas (Branding) para Frontend Desacoplado.

Este backend sirve configuraciones de temas visuales incluyendo:
- Colores de marca
- Fuentes con CSS generado dinámicamente
- Logos e imágenes
- Placeholders para diferentes categorías

La arquitectura está diseñada para migrar fácilmente a un CDN
mediante la variable de entorno STATIC_BASE_URL.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.theme import router as theme_router
from app.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    # Startup
    settings = get_settings()
    print(f"🚀 Theme Backend starting...")
    print(f"📁 Static files: {settings.STATIC_DIR}")
    print(f"🌐 Static base URL: {settings.STATIC_BASE_URL}")
    print(f"💾 Cache enabled: {settings.ENABLE_CACHE}")
    yield
    # Shutdown
    print("👋 Theme Backend shutting down...")


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="Theme Backend API",
        description="""
        API para servir temas visuales (branding) a frontends desacoplados.

        ## Características
        - Configuración de colores por marca
        - Fuentes con CSS generado dinámicamente
        - URLs de logos y placeholders
        - Cache en memoria para rendimiento
        - Preparado para migración a CDN

        ## Uso
        1. Obtener tema: `GET /api/theme/{brandId}`
        2. CSS de fuentes: `GET /api/fonts/{brandId}/fonts.css`
        3. Listar brands: `GET /api/brands`
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS - Permitir todos los orígenes en desarrollo
    # En producción, configurar orígenes específicos
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Montar archivos estáticos
    static_dir = settings.STATIC_DIR
    if os.path.exists(static_dir):
        app.mount(
            "/static",
            StaticFiles(directory=static_dir),
            name="static"
        )
    else:
        print(f"⚠️  Warning: Static directory not found: {static_dir}")

    # Registrar routers
    app.include_router(theme_router)

    return app


# Crear instancia de la aplicación
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
