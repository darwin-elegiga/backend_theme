#!/usr/bin/env python3
"""
Script para convertir fuentes OTF/TTF a WOFF2 para un brand específico.

Uso:
    python3 scripts/convert_fonts.py mapfre
    python3 scripts/convert_fonts.py --all
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from font_converter import FontConverter


def convert_brand_fonts(brand_id: str, base_dir: Path) -> None:
    """Convierte las fuentes de un brand específico."""
    fonts_dir = base_dir / "static" / "brands" / brand_id / "fonts"

    if not fonts_dir.exists():
        print(f"Error: No existe el directorio {fonts_dir}")
        return

    # Buscar archivos OTF/TTF
    otf_files = list(fonts_dir.glob("*.otf")) + list(fonts_dir.glob("*.ttf"))

    if not otf_files:
        print(f"No se encontraron fuentes OTF/TTF en {fonts_dir}")
        return

    print(f"\n{'='*50}")
    print(f"Convirtiendo fuentes para: {brand_id}")
    print(f"{'='*50}")
    print(f"Directorio: {fonts_dir}")
    print(f"Fuentes encontradas: {len(otf_files)}")

    converter = FontConverter(
        input_dir=str(fonts_dir),
        output_dir=str(fonts_dir)  # Mismo directorio
    )

    processed = converter.process_fonts()

    print(f"\n✓ Convertidas {len(processed)} fuentes")
    print(f"  Los archivos WOFF2 están en: {fonts_dir}")


def main():
    base_dir = Path(__file__).parent.parent
    brands_dir = base_dir / "static" / "brands"

    if len(sys.argv) < 2:
        print("Uso: python3 scripts/convert_fonts.py <brand_id>")
        print("      python3 scripts/convert_fonts.py --all")
        print("\nBrands disponibles:")
        for brand in brands_dir.iterdir():
            if brand.is_dir():
                print(f"  - {brand.name}")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Convertir todas las marcas
        for brand_dir in brands_dir.iterdir():
            if brand_dir.is_dir():
                convert_brand_fonts(brand_dir.name, base_dir)
    else:
        # Convertir marca específica
        brand_id = sys.argv[1].lower()
        convert_brand_fonts(brand_id, base_dir)


if __name__ == "__main__":
    main()
