from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from pathlib import Path
import shutil
from typing import List, Dict, Any
import hashlib


class FontConverter:
    """Convierte fuentes OTF a formatos web (WOFF2, WOFF)"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_otf_to_web_formats(self, otf_path: Path) -> Dict[str, Path]:
        """
        Convierte un archivo OTF a WOFF2 y WOFF
        
        Args:
            otf_path: Ruta al archivo OTF
            
        Returns:
            Diccionario con las rutas de los archivos generados
        """
        results = {}
        base_name = otf_path.stem
        
        try:
            # Cargar la fuente
            font = TTFont(otf_path)
            
            # Convertir a WOFF2 (formato más eficiente)
            woff2_path = self.output_dir / f"{base_name}.woff2"
            font.flavor = 'woff2'
            font.save(woff2_path)
            results['woff2'] = woff2_path
            print(f"✓ Generado: {woff2_path.name}")
            
            # Recargar para WOFF (mejor compatibilidad)
            font = TTFont(otf_path)
            woff_path = self.output_dir / f"{base_name}.woff"
            font.flavor = 'woff'
            font.save(woff_path)
            results['woff'] = woff_path
            print(f"✓ Generado: {woff_path.name}")
            
            font.close()
            
        except Exception as e:
            print(f"✗ Error convirtiendo {otf_path.name}: {str(e)}")
            raise
        
        return results
    
    def extract_font_metadata(self, font_path: Path) -> Dict[str, Any]:
        """Extrae metadata de la fuente (peso, estilo, nombre)"""
        try:
            font = TTFont(font_path)
            
            # Obtener nombre de la fuente
            name_table = font['name']
            font_family = name_table.getDebugName(1)  # Family name
            font_subfamily = name_table.getDebugName(2)  # Subfamily name
            
            # Determinar peso y estilo
            weight = 400  # Regular por defecto
            style = "normal"
            
            subfamily_lower = font_subfamily.lower() if font_subfamily else ""
            
            if 'thin' in subfamily_lower or 'hairline' in subfamily_lower:
                weight = 100
            elif 'extralight' in subfamily_lower or 'ultralight' in subfamily_lower:
                weight = 200
            elif 'light' in subfamily_lower:
                weight = 300
            elif 'medium' in subfamily_lower:
                weight = 500
            elif 'semibold' in subfamily_lower or 'demibold' in subfamily_lower:
                weight = 600
            elif 'bold' in subfamily_lower:
                weight = 700
            elif 'extrabold' in subfamily_lower or 'ultrabold' in subfamily_lower:
                weight = 800
            elif 'black' in subfamily_lower or 'heavy' in subfamily_lower:
                weight = 900
            
            if 'italic' in subfamily_lower or 'oblique' in subfamily_lower:
                style = "italic"
            
            font.close()
            
            return {
                "name": font_family,
                "subfamily": font_subfamily,
                "weight": weight,
                "style": style
            }
        
        except Exception as e:
            print(f"⚠ Error extrayendo metadata de {font_path.name}: {str(e)}")
            return {
                "name": font_path.stem,
                "weight": 400,
                "style": "normal"
            }
    
    def process_fonts(self) -> List[Dict[str, Any]]:
        """
        Procesa todas las fuentes OTF en el directorio de entrada
        
        Returns:
            Lista de diccionarios con información de las fuentes procesadas
        """
        processed_fonts = []
        
        otf_files = list(self.input_dir.glob("*.otf"))
        otf_files.extend(self.input_dir.glob("*.ttf"))
        
        if not otf_files:
            print(f"⚠ No se encontraron archivos OTF/TTF en {self.input_dir}")
            return processed_fonts
        
        print(f"\n📦 Procesando {len(otf_files)} fuentes...\n")
        
        for font_file in otf_files:
            print(f"Procesando: {font_file.name}")
            
            try:
                # Extraer metadata
                metadata = self.extract_font_metadata(font_file)
                
                # Convertir a formatos web
                converted_files = self.convert_otf_to_web_formats(font_file)
                
                # Guardar información
                font_info = {
                    "original": font_file.name,
                    "name": metadata["name"],
                    "weight": metadata["weight"],
                    "style": metadata["style"],
                    "files": {
                        "woff2": converted_files.get('woff2', Path()).name if 'woff2' in converted_files else None,
                        "woff": converted_files.get('woff', Path()).name if 'woff' in converted_files else None
                    }
                }
                
                processed_fonts.append(font_info)
                print(f"✓ Completado: {font_file.name}\n")
                
            except Exception as e:
                print(f"✗ Error procesando {font_file.name}: {str(e)}\n")
        
        return processed_fonts
    
    def generate_font_config(self, processed_fonts: List[Dict[str, Any]], 
                            customer_name: str = "default") -> Dict[str, Any]:
        """
        Genera la configuración de fuentes para el tema
        
        Args:
            processed_fonts: Lista de fuentes procesadas
            customer_name: Nombre del cliente
            
        Returns:
            Diccionario con la configuración de fuentes
        """
        # Agrupar fuentes por familia
        font_families = {}
        
        for font in processed_fonts:
            family_name = font['name']
            if family_name not in font_families:
                font_families[family_name] = []
            font_families[family_name].append(font)
        
        # Construir configuración
        fonts_config = {}
        
        families = list(font_families.keys())
        if len(families) > 0:
            # Primera familia como primaria
            primary_family = families[0]
            fonts_config['primary'] = {
                "name": primary_family,
                "variants": [
                    {
                        "src": font['files']['woff2'],
                        "weight": font['weight'],
                        "style": font['style']
                    }
                    for font in font_families[primary_family]
                ]
            }
        
        if len(families) > 1:
            # Segunda familia como secundaria
            secondary_family = families[1]
            fonts_config['secondary'] = {
                "name": secondary_family,
                "variants": [
                    {
                        "src": font['files']['woff2'],
                        "weight": font['weight'],
                        "style": font['style']
                    }
                    for font in font_families[secondary_family]
                ]
            }
        
        fonts_config['fallback'] = "Arial, sans-serif"
        
        return fonts_config


if __name__ == "__main__":
    # Ejemplo de uso
    converter = FontConverter(
        input_dir="/app/fonts/input",
        output_dir="/app/fonts"
    )
    
    processed = converter.process_fonts()
    
    if processed:
        config = converter.generate_font_config(processed)
        print("\n" + "="*50)
        print("Configuración generada:")
        print("="*50)
        import json
        print(json.dumps(config, indent=2))
    else:
        print("\n⚠ No se procesaron fuentes")