# Theme API - Sistema de Gestión de Temas y Fuentes

API REST para servir configuraciones de temas personalizados y gestionar fuentes tipográficas con conversión automática de OTF a formatos web.

## 🚀 Características

- ✅ Conversión automática de fuentes OTF/TTF a WOFF2 y WOFF
- ✅ API REST para obtener temas por cliente
- ✅ Servicio de archivos estáticos para fuentes
- ✅ Configuración JSON flexible para cada cliente
- ✅ Docker y Docker Compose para despliegue fácil
- ✅ Hot reload para desarrollo
- ✅ CORS configurado

## 📁 Estructura del Proyecto

```
theme-api/
├── main.py                    # API principal FastAPI
├── font_converter.py          # Conversor de fuentes
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Orquestación
├── requirements.txt           # Dependencias Python
├── fonts/
│   ├── input/                 # Fuentes OTF/TTF originales
│   └── output/                # Fuentes convertidas (WOFF2, WOFF)
└── themes/
    ├── santander.json         # Configuración tema Santander
    └── [cliente].json         # Más configuraciones
```

## 🔧 Instalación

### Prerrequisitos

- Docker
- Docker Compose

### Pasos de Instalación

1. **Clonar o crear la estructura del proyecto:**

```bash
mkdir theme-api && cd theme-api
mkdir -p fonts/input fonts/output themes
```

2. **Crear los archivos del proyecto:**
   - `main.py`
   - `font_converter.py`
   - `Dockerfile`
   - `docker-compose.yml`
   - `requirements.txt`

3. **Construir y ejecutar con Docker Compose:**

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`

## 📝 Uso

### 1. Convertir Fuentes OTF a Web Fonts

Coloca tus archivos `.otf` o `.ttf` en la carpeta `fonts/input/`:

```bash
cp MiFuente-Regular.otf fonts/input/
cp MiFuente-Bold.otf fonts/input/
```

Ejecuta el conversor:

```bash
docker-compose exec theme-api python font_converter.py
```

Las fuentes convertidas aparecerán en `fonts/output/` en formatos WOFF2 y WOFF.

### 2. Crear Configuración de Tema

Crea un archivo JSON en `themes/` con el nombre del cliente:

**themes/micliente.json:**

```json
{
  "colors": {
    "primary": "#0066CC",
    "secondary": "#333333",
    "background": "#FFFFFF",
    "text": "#1A1A1A"
  },
  "fonts": {
    "primary": {
      "name": "Mi Fuente Principal",
      "variants": [
        {
          "src": "MiFuente-Regular.woff2",
          "weight": 400,
          "style": "normal"
        },
        {
          "src": "MiFuente-Bold.woff2",
          "weight": 700,
          "style": "normal"
        }
      ]
    },
    "fallback": "Arial, sans-serif"
  },
  "logos": {
    "header": "https://micdn.com/logo.svg",
    "favicon": "https://micdn.com/favicon.ico"
  }
}
```

### 3. Consumir la API

#### Obtener tema de un cliente:

```bash
curl http://localhost:8000/api/theme/santander
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "customerName": "santander",
    "colors": { ... },
    "fonts": {
      "primary": {
        "name": "Santander Headline",
        "variants": [
          {
            "src": "http://localhost:8000/fonts/SantanderHeadline-Regular.woff2",
            "weight": 400,
            "style": "normal"
          }
        ]
      }
    },
    "logos": { ... },
    "placeholders": { ... }
  }
}
```

#### Listar todos los temas disponibles:

```bash
curl http://localhost:8000/api/themes
```

#### Acceder directamente a una fuente:

```
http://localhost:8000/fonts/MiFuente-Regular.woff2
```

## 🔌 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Health check |
| GET | `/api/theme/{customer_name}` | Obtener tema de un cliente |
| GET | `/api/themes` | Listar todos los temas |
| GET | `/fonts/{filename}` | Descargar fuente |

## 🎨 Uso en Frontend

### React/Next.js

```javascript
// Obtener tema
const response = await fetch('http://localhost:8000/api/theme/santander');
const { data } = await response.json();

// Aplicar fuentes dinámicamente
const loadFonts = (fonts) => {
  const style = document.createElement('style');
  
  Object.values(fonts).forEach(fontFamily => {
    if (fontFamily.variants) {
      fontFamily.variants.forEach(variant => {
        style.innerHTML += `
          @font-face {
            font-family: '${fontFamily.name}';
            src: url('${variant.src}') format('woff2');
            font-weight: ${variant.weight};
            font-style: ${variant.style};
          }
        `;
      });
    }
  });
  
  document.head.appendChild(style);
};

loadFonts(data.fonts);

// Aplicar colores
document.documentElement.style.setProperty('--color-primary', data.colors.primary);
```

### CSS Variables

```css
:root {
  --font-primary: 'Santander Headline', Arial, sans-serif;
  --color-primary: #EC0000;
}

body {
  font-family: var(--font-primary);
  color: var(--color-primary);
}
```

## 🛠️ Desarrollo

### Variables de Entorno

Puedes configurar en `docker-compose.yml`:

```yaml
environment:
  - BASE_URL=http://localhost:8000  # URL base para las fuentes
  - PYTHONUNBUFFERED=1
```

### Hot Reload

El código está montado como volumen, los cambios se reflejan automáticamente.

### Logs

```bash
docker-compose logs -f theme-api
```

## 📦 Producción

Para producción, modifica `docker-compose.yml`:

```yaml
environment:
  - BASE_URL=https://tu-dominio.com
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 🧪 Testing

Prueba los endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Obtener tema
curl http://localhost:8000/api/theme/santander | jq

# Listar temas
curl http://localhost:8000/api/themes | jq
```

## 📚 Metadata de Fuentes

El conversor extrae automáticamente:

- **Nombre de la familia tipográfica**
- **Peso (weight)**: 100-900
- **Estilo**: normal, italic
- **Formato**: WOFF2 (mayor compresión) y WOFF (compatibilidad)

## 🔒 Seguridad

- ✅ CORS configurado (ajusta según necesidad)
- ✅ Solo lectura de archivos estáticos
- ⚠️ En producción, restringe orígenes CORS
- ⚠️ Implementa autenticación si es necesario

## 📄 Licencia

MIT

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

---

**¿Necesitas ayuda?** Revisa los logs con `docker-compose logs -f`