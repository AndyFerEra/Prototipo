import os
import uuid
from pathlib import Path
import pandas as pd

UPLOAD_DIR = Path("assets") / "uploads"
EXCEL_DIR = UPLOAD_DIR / "excel"

# Crear directorios si no existen
EXCEL_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_excel(file_content: bytes, original_filename: str) -> str:
    """Guarda un Excel subido y devuelve la ruta relativa"""
    filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = EXCEL_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)

def read_excel_file(file_path: str) -> dict:
    """Lee un archivo Excel y devuelve un diccionario con los datos de todas las hojas"""
    try:
        excel_file = pd.ExcelFile(file_path)
        sheets_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheets_data[sheet_name] = {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records')
            }
        
        return sheets_data
    except Exception as e:
        print(f"Error leyendo Excel: {e}")
        return {}