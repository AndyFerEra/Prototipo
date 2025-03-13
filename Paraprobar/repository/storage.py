import os
import uuid
import io
import shutil
from pathlib import Path
import reflex as rx


UPLOAD_DIR = Path("assets") / "uploads"
PDF_DIR = UPLOAD_DIR / "pdfs"
EXCEL_DIR = UPLOAD_DIR / "excel"


PDF_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_pdf(file_content: bytes, original_filename: str) -> str:
    """PDF subido y devuelve la ruta relativa"""
    filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = PDF_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return f"/uploads/pdfs/{filename}"

def save_uploaded_excel(file_content: bytes, original_filename: str) -> str:
    """Excel subido y devuelve la ruta relativa"""
    filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = EXCEL_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return f"/uploads/excel/{filename}"

def get_file_list(directory: Path) -> list[dict]:
    """lista de archivos en el directorio especificado"""
    files = []
    if directory.exists():
        for file in directory.iterdir():
            if file.is_file():
                files.append({
                    "name": file.name,
                    "path": f"/uploads/{directory.name}/{file.name}",
                    "size": file.stat().st_size,
                    "modified": file.stat().st_mtime
                })
    return files