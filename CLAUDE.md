# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend that serves visual theme configurations (branding) for decoupled frontends. Each brand (e.g., mapfre, santander) has its own color palette, fonts, logos, and placeholder images. The architecture supports easy migration to CDN via `STATIC_BASE_URL`.

## Common Commands

```bash
# Run locally (development with hot reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run with Docker
docker-compose up --build

# Run dev profile (cache disabled, port 8001)
docker-compose --profile dev up theme-api-dev

# Test API endpoints
./scripts/test_api.sh [BASE_URL]

# Convert fonts (OTF/TTF to WOFF2)
python3 scripts/convert_fonts.py mapfre
python3 scripts/convert_fonts.py --all
```

## Architecture

```
app/
├── main.py                    # FastAPI app factory, CORS, static files mount
├── config/
│   ├── settings.py            # Pydantic settings (env vars, caching)
│   └── brands.json            # Brand configurations (colors, fonts, placeholders)
├── api/
│   └── theme.py               # API endpoints (/api/theme/{brand_id}, /api/fonts, /api/brands)
├── models/
│   └── theme_response.py      # Pydantic response models (ThemeData, Colors, Fonts, etc.)
└── services/
    ├── brand_service.py       # Loads brands.json, builds public URLs for assets
    └── font_service.py        # Generates @font-face CSS dynamically
```

## API Endpoints (Frontend Reference)

Base URL: `http://localhost:8000` (desarrollo) | CDN URL (producción)

---

### 1. Obtener Tema Completo

```
GET /api/theme/{brand_id}
```

**Parámetros:**
- `brand_id` (path): Identificador del brand (`mapfre`, `santander`)

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "customerName": "mapfre",
    "colors": {
      "primary": "#D81E05",
      "primaryDisabled": "#d81e059d",
      "secondary": "#1A1A1A",
      "link": "#D81E05",
      "background": "#FFFFFF",
      "backgroundSecondary": "#F5F5F5",
      "headerBackground": "#D81E05",
      "navBar": "#D81E05",
      "navBarSecondary": "#B30000",
      "text": "#1A1A1A",
      "textSecondary": "#666666",
      "border": "#E0E0E0",
      "overlay": "rgba(0, 0, 0, 0.4)",
      "error": "#D32F2F",
      "errorBackground": "#FFEBEE",
      "errorText": "#D32F2F",
      "success": "#2E7D32",
      "warning": "#F57C00",
      "buttonNext": "#D81E05",
      "buttonNextText": "#FFFFFF",
      "buttonBack": "transparent",
      "buttonBackText": "#D81E05"
    },
    "fonts": {
      "primary": {
        "name": "Mapfre Sans",
        "variants": [
          { "src": "http://localhost:8000/static/brands/mapfre/fonts/MapfreSans-Light.woff2", "weight": 300, "style": "normal" },
          { "src": "http://localhost:8000/static/brands/mapfre/fonts/MapfreSans-Regular.woff2", "weight": 400, "style": "normal" },
          { "src": "http://localhost:8000/static/brands/mapfre/fonts/MapfreSans-Bold.woff2", "weight": 700, "style": "normal" }
        ]
      },
      "secondary": {
        "name": "Mapfre Text",
        "variants": [
          { "src": "...", "weight": 400, "style": "normal" }
        ]
      },
      "fallback": "Arial, sans-serif",
      "cssUrl": "http://localhost:8000/api/fonts/mapfre/fonts.css"
    },
    "logos": {
      "header": "http://localhost:8000/static/brands/mapfre/images/logo.svg",
      "favicon": "http://localhost:8000/static/brands/mapfre/images/favicon.ico"
    },
    "placeholders": {
      "car": {
        "front": "http://localhost:8000/static/brands/mapfre/images/placeholders/car/car-illustration-front.png",
        "frontRight": "http://localhost:8000/static/brands/mapfre/images/placeholders/car/car-illustration-front-right.png",
        "right": "...",
        "rearRight": "...",
        "rear": "...",
        "rearLeft": "...",
        "left": "...",
        "frontLeft": "..."
      },
      "moto": {
        "front": "...",
        "right": "...",
        "rear": "...",
        "left": "..."
      },
      "odometer": {
        "mileage": "http://localhost:8000/static/brands/mapfre/images/placeholders/odometer/odometer-illustration.png"
      },
      "documentation": {
        "dniIllustrationFront": "...",
        "dniIllustrationBack": "...",
        "dniPhotoFront": "...",
        "dniPhotoBack": "...",
        "licenseIllustrationFront": "...",
        "licenseIllustrationBack": "...",
        "licensePhotoFront": "...",
        "licensePhotoBack": "...",
        "dataSheetIllustrationFront": "...",
        "dataSheetIllustrationBack": "...",
        "dataSheetPhotoFront": "...",
        "dataSheetPhotoBack": "...",
        "circulationIllustrationFront": "...",
        "circulationIllustrationBack": "...",
        "circulationPhotoFront": "...",
        "circulationPhotoBack": "..."
      }
    }
  }
}
```

**Error (404) - Brand no encontrado:**
```json
{
  "detail": {
    "success": false,
    "error": "Brand not found",
    "detail": "The brand 'xxx' does not exist. Available brands: mapfre, santander"
  }
}
```

**Ejemplo frontend (React/Next.js):**
```javascript
const response = await fetch('http://localhost:8000/api/theme/mapfre');
const { data } = await response.json();

// Aplicar colores como CSS variables
Object.entries(data.colors).forEach(([key, value]) => {
  document.documentElement.style.setProperty(`--color-${key}`, value);
});

// Cargar CSS de fuentes
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = data.fonts.cssUrl;
document.head.appendChild(link);
```

---

### 2. CSS de Fuentes (Dinámico)

```
GET /api/fonts/{brand_id}/fonts.css
```

**Parámetros:**
- `brand_id` (path): Identificador del brand

**Respuesta (200):** `Content-Type: text/css`
```css
/* Fonts for mapfre */
/* Generated dynamically - DO NOT EDIT */

/* Primary Font: Mapfre Sans */
@font-face {
  font-family: 'Mapfre Sans';
  src: url('http://localhost:8000/static/brands/mapfre/fonts/MapfreSans-Light.woff2') format('woff2');
  font-weight: 300;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Mapfre Sans';
  src: url('http://localhost:8000/static/brands/mapfre/fonts/MapfreSans-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

/* ... más variantes ... */

/* CSS Custom Properties */
:root {
  --font-primary: 'Mapfre Sans', Arial, sans-serif;
  --font-secondary: 'Mapfre Text', Arial, sans-serif;
  --font-fallback: Arial, sans-serif;
}
```

**Uso en HTML:**
```html
<link rel="stylesheet" href="http://localhost:8000/api/fonts/mapfre/fonts.css">
```

---

### 3. Listar Brands Disponibles

```
GET /api/brands
```

**Respuesta (200):**
```json
{
  "success": true,
  "brands": ["mapfre", "santander"]
}
```

---

### 4. Health Check

```
GET /api/health
```

**Respuesta (200):**
```json
{
  "status": "healthy",
  "service": "theme-api"
}
```

---

### 5. Archivos Estáticos

```
GET /static/brands/{brand_id}/{path}
```

Acceso directo a archivos estáticos (imágenes, fuentes).

**Ejemplos:**
```
GET /static/brands/mapfre/images/logo.svg
GET /static/brands/mapfre/fonts/MapfreSans-Regular.woff2
GET /static/brands/mapfre/images/placeholders/car/car-illustration-front.png
```

---

### Documentación Interactiva

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Adding a New Brand

1. Add brand entry in `app/config/brands.json` with colors, fonts, logos, placeholders
2. Create static assets in `static/brands/{brand_id}/`:
   - `fonts/` - WOFF2 font files
   - `images/` - logo.svg, favicon.ico
   - `images/placeholders/` - car/, moto/, odometer/, documentation/
3. Run font conversion if needed: `python3 scripts/convert_fonts.py {brand_id}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STATIC_BASE_URL` | `http://localhost:8000/static` | Base URL for assets (use CDN in prod) |
| `CORS_ORIGINS` | `*` | Allowed origins (comma-separated) |
| `ENABLE_CACHE` | `true` | In-memory cache for configs |
| `CACHE_TTL` | `3600` | Cache TTL in seconds |
