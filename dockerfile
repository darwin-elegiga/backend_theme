# Dockerfile para Theme Backend
# Python 3.11 slim - Multi-stage build para optimizar tamaño

# =============================================================================
# Stage 1: Builder - Instala dependencias
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema para compilar paquetes (fonttools, brotli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# =============================================================================
# Stage 2: Production - Imagen final optimizada
# =============================================================================
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Theme Backend"
LABEL description="FastAPI backend for serving brand themes"
LABEL version="1.0"

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/appuser/.local

# Asegurar que los binarios estén en PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar código de la aplicación
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser static/ ./static/

# Crear directorios necesarios con permisos correctos
RUN mkdir -p /app/static/brands && chown -R appuser:appuser /app/static

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATIC_BASE_URL=http://localhost:8000/static \
    CORS_ORIGINS=* \
    ENABLE_CACHE=true \
    CACHE_TTL=3600

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Comando de inicio (producción)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
