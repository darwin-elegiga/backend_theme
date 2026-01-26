"""
Admin API routes for managing brand themes.
REST API + HTML panel for development.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config.settings import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Paths
settings = get_settings()
BRANDS_JSON_PATH = Path(__file__).parent.parent / "config" / "brands.json"
STATIC_DIR = Path(__file__).parent.parent.parent / "static" / "brands"


# ============================================================================
# Pydantic Models for API
# ============================================================================

class ColorsUpdate(BaseModel):
    """Model for updating colors."""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    link: Optional[str] = None
    background: Optional[str] = None
    backgroundSecondary: Optional[str] = None
    headerBackground: Optional[str] = None
    navBar: Optional[str] = None
    navBarSecondary: Optional[str] = None
    text: Optional[str] = None
    textSecondary: Optional[str] = None
    overlay: Optional[str] = None
    error: Optional[str] = None
    errorBackground: Optional[str] = None
    errorText: Optional[str] = None
    success: Optional[str] = None
    warning: Optional[str] = None
    buttonNext: Optional[str] = None
    buttonNextDisabled: Optional[str] = None
    buttonNextText: Optional[str] = None
    buttonBack: Optional[str] = None
    buttonBackDisabled: Optional[str] = None
    buttonBackText: Optional[str] = None
    skeleton: Optional[str] = None


class BrandCreate(BaseModel):
    """Model for creating a new brand."""
    brand_id: str
    customer_name: str
    copy_from: Optional[str] = None  # Copy config from existing brand


class FontVariantInput(BaseModel):
    """Font variant input."""
    weight: int
    style: str = "normal"


# ============================================================================
# Helper Functions
# ============================================================================

def load_brands() -> Dict[str, Any]:
    """Load brands.json file."""
    with open(BRANDS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_brands(data: Dict[str, Any]) -> None:
    """Save brands.json file."""
    with open(BRANDS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Clear cache if enabled
    from app.services.brand_service import get_brand_service
    service = get_brand_service()
    service._brands_cache = None


def get_brand_static_dir(brand_id: str) -> Path:
    """Get static directory for a brand."""
    return STATIC_DIR / brand_id


def ensure_brand_dirs(brand_id: str) -> None:
    """Ensure all directories exist for a brand."""
    brand_dir = get_brand_static_dir(brand_id)
    dirs = [
        brand_dir / "fonts",
        brand_dir / "images",
        brand_dir / "images" / "placeholders" / "car",
        brand_dir / "images" / "placeholders" / "moto",
        brand_dir / "images" / "placeholders" / "odometer",
        brand_dir / "images" / "placeholders" / "documentation",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


# ============================================================================
# HTML Panel
# ============================================================================

@router.get("", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Render admin HTML panel."""
    brands = load_brands()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "brands": list(brands.keys()),
            "static_base_url": settings.STATIC_BASE_URL,
        }
    )


# ============================================================================
# Brands CRUD API
# ============================================================================

@router.get("/api/brands")
async def list_brands():
    """List all available brands."""
    brands = load_brands()
    return {"success": True, "brands": list(brands.keys())}


@router.get("/api/brands/{brand_id}")
async def get_brand(brand_id: str):
    """Get complete brand configuration."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")
    return {"success": True, "data": brands[brand_id]}


@router.put("/api/brands/{brand_id}")
async def update_brand(brand_id: str, config: Dict[str, Any]):
    """Update complete brand configuration."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    brands[brand_id] = config
    save_brands(brands)
    return {"success": True}


@router.patch("/api/brands/{brand_id}/colors")
async def update_colors(brand_id: str, colors: ColorsUpdate):
    """Update only brand colors."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Update only provided colors
    colors_dict = colors.model_dump(exclude_none=True)
    brands[brand_id]["colors"].update(colors_dict)
    save_brands(brands)
    return {"success": True}


@router.post("/api/brands")
async def create_brand(brand_data: BrandCreate):
    """Create a new brand."""
    brands = load_brands()

    if brand_data.brand_id in brands:
        raise HTTPException(status_code=400, detail=f"Brand '{brand_data.brand_id}' already exists")

    if brand_data.copy_from:
        if brand_data.copy_from not in brands:
            raise HTTPException(status_code=404, detail=f"Source brand '{brand_data.copy_from}' not found")
        # Copy from existing brand
        new_config = json.loads(json.dumps(brands[brand_data.copy_from]))
        new_config["customerName"] = brand_data.customer_name
    else:
        # Create minimal config
        new_config = {
            "customerName": brand_data.customer_name,
            "colors": {
                "primary": "#000000",
                "secondary": "#333333",
                "link": "#0066CC",
                "background": "#FFFFFF",
                "backgroundSecondary": "#F5F5F5",
                "headerBackground": "#000000",
                "navBar": "#000000",
                "navBarSecondary": "#333333",
                "text": "#1A1A1A",
                "textSecondary": "#666666",
                "overlay": "rgba(0, 0, 0, 0.4)",
                "error": "#D32F2F",
                "errorBackground": "#FFEBEE",
                "errorText": "#D32F2F",
                "success": "#2E7D32",
                "warning": "#F57C00",
                "buttonNext": "#000000",
                "buttonNextDisabled": "#00000066",
                "buttonNextText": "#FFFFFF",
                "buttonBack": "transparent",
                "buttonBackDisabled": "#E0E0E0",
                "buttonBackText": "#000000",
                "skeleton": "#E0E0E0"
            },
            "fonts": {
                "primary": {
                    "name": "Arial",
                    "variants": []
                },
                "fallback": "Arial, sans-serif"
            },
            "logos": {
                "header": "logo.svg",
                "favicon": "favicon.ico"
            },
            "placeholders": {
                "car": {},
                "moto": {},
                "odometer": {},
                "documentation": {}
            }
        }

    brands[brand_data.brand_id] = new_config
    save_brands(brands)

    # Create directories
    ensure_brand_dirs(brand_data.brand_id)

    return {"success": True, "id": brand_data.brand_id}


@router.delete("/api/brands/{brand_id}")
async def delete_brand(brand_id: str):
    """Delete a brand."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    del brands[brand_id]
    save_brands(brands)

    # Optionally delete static files (commented for safety)
    # shutil.rmtree(get_brand_static_dir(brand_id), ignore_errors=True)

    return {"success": True}


# ============================================================================
# Upload API
# ============================================================================

@router.post("/api/brands/{brand_id}/logo")
async def upload_logo(brand_id: str, file: UploadFile = File(...)):
    """Upload brand logo."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Validate file type
    allowed_extensions = [".svg", ".png"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")

    # Save file
    brand_dir = get_brand_static_dir(brand_id)
    images_dir = brand_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    filename = f"logo{ext}"
    filepath = images_dir / filename

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update brands.json
    brands[brand_id]["logos"]["header"] = filename
    save_brands(brands)

    return {"success": True, "filename": filename}


@router.post("/api/brands/{brand_id}/favicon")
async def upload_favicon(brand_id: str, file: UploadFile = File(...)):
    """Upload brand favicon."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Validate file type
    allowed_extensions = [".ico", ".png"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")

    # Save file
    brand_dir = get_brand_static_dir(brand_id)
    images_dir = brand_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    filename = f"favicon{ext}"
    filepath = images_dir / filename

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update brands.json
    brands[brand_id]["logos"]["favicon"] = filename
    save_brands(brands)

    return {"success": True, "filename": filename}


@router.post("/api/brands/{brand_id}/placeholder/{category}/{name}")
async def upload_placeholder(
    brand_id: str,
    category: str,
    name: str,
    file: UploadFile = File(...)
):
    """Upload placeholder image."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Validate category
    valid_categories = ["car", "moto", "odometer", "documentation"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Allowed: {valid_categories}")

    # Validate file type
    allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".avif"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")

    # Save file
    brand_dir = get_brand_static_dir(brand_id)
    placeholder_dir = brand_dir / "images" / "placeholders" / category
    placeholder_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename based on category and name
    filename = f"{category}-illustration-{name}{ext}"
    filepath = placeholder_dir / filename

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update brands.json
    relative_path = f"{category}/{filename}"
    if category not in brands[brand_id]["placeholders"]:
        brands[brand_id]["placeholders"][category] = {}
    brands[brand_id]["placeholders"][category][name] = relative_path
    save_brands(brands)

    return {"success": True, "filename": filename, "path": relative_path}


@router.post("/api/brands/{brand_id}/font")
async def upload_font(
    brand_id: str,
    file: UploadFile = File(...),
    font_type: str = Form("primary"),  # primary or secondary
    font_name: str = Form(...),
    weight: int = Form(400),
    style: str = Form("normal")
):
    """Upload font file (OTF/TTF) and convert to WOFF2."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    # Validate file type
    allowed_extensions = [".otf", ".ttf", ".woff2"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")

    # Validate font_type
    if font_type not in ["primary", "secondary"]:
        raise HTTPException(status_code=400, detail="font_type must be 'primary' or 'secondary'")

    # Save original file
    brand_dir = get_brand_static_dir(brand_id)
    fonts_dir = brand_dir / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    style_suffix = "-Italic" if style == "italic" else ""
    weight_names = {
        100: "Thin", 200: "ExtraLight", 300: "Light",
        400: "Regular", 500: "Medium", 600: "SemiBold",
        700: "Bold", 800: "ExtraBold", 900: "Black"
    }
    weight_name = weight_names.get(weight, f"W{weight}")
    base_filename = f"{font_name.replace(' ', '')}-{weight_name}{style_suffix}"

    # Save and convert
    if ext in [".otf", ".ttf"]:
        # Save original
        original_path = fonts_dir / f"{base_filename}{ext}"
        with open(original_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Convert to WOFF2
        try:
            from fontTools.ttLib import TTFont

            font = TTFont(str(original_path))
            woff2_path = fonts_dir / f"{base_filename}.woff2"
            font.flavor = "woff2"
            font.save(str(woff2_path))
            font.close()

            # Remove original
            original_path.unlink()

            final_filename = f"{base_filename}.woff2"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Font conversion failed: {str(e)}")
    else:
        # Already WOFF2
        final_filename = f"{base_filename}.woff2"
        filepath = fonts_dir / final_filename
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

    # Update brands.json
    font_config = brands[brand_id]["fonts"]

    if font_type not in font_config or font_config[font_type] is None:
        font_config[font_type] = {
            "name": font_name,
            "variants": []
        }

    font_config[font_type]["name"] = font_name

    # Check if variant already exists
    variants = font_config[font_type]["variants"]
    existing = next(
        (v for v in variants if v["weight"] == weight and v["style"] == style),
        None
    )

    if existing:
        existing["file"] = final_filename
    else:
        variants.append({
            "file": final_filename,
            "weight": weight,
            "style": style
        })

    # Sort variants by weight
    font_config[font_type]["variants"] = sorted(variants, key=lambda x: (x["weight"], x["style"]))

    save_brands(brands)

    return {
        "success": True,
        "filename": final_filename,
        "font_type": font_type,
        "weight": weight,
        "style": style
    }


@router.delete("/api/brands/{brand_id}/font/{font_type}/{weight}/{style}")
async def delete_font_variant(brand_id: str, font_type: str, weight: int, style: str):
    """Delete a font variant."""
    brands = load_brands()
    if brand_id not in brands:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    font_config = brands[brand_id]["fonts"]
    if font_type not in font_config or font_config[font_type] is None:
        raise HTTPException(status_code=404, detail=f"Font type '{font_type}' not found")

    variants = font_config[font_type]["variants"]
    original_len = len(variants)

    # Find and remove variant
    font_config[font_type]["variants"] = [
        v for v in variants
        if not (v["weight"] == weight and v["style"] == style)
    ]

    if len(font_config[font_type]["variants"]) == original_len:
        raise HTTPException(status_code=404, detail="Font variant not found")

    save_brands(brands)
    return {"success": True}
