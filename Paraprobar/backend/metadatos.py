import os
import fitz  # PyMuPDF
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Session, create_engine, select
from urllib.parse import quote_plus


# ⚙️ Ruta donde tienes los PDFs
carpeta_pdfs = r"C:\Users\Usuario\Desktop\DATOS"

# ✅ Definir el modelo de metadatos directamente aquí
class MetadatosPDF(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    archivo: Optional[str]
    titulo: Optional[str]
    autor: Optional[str]
    asunto: Optional[str]
    palabras_clave: Optional[str]
    creador: Optional[str]
    fecha_creacion: Optional[str]
    fecha_modificacion: Optional[str]
    numero_paginas: Optional[int]

# 🔌 Conexión a la base de datos (ajusta si no es SQLite)
# Reemplaza esto si usas SQL Server (ya que eso mencionaste antes)
# Codificar la contraseña (por el carácter @)
password = "12345"
encoded_password = quote_plus(password)
DATABASE_URL = rf"mssql+pyodbc://sa:{encoded_password}@DESKTOP-L84HKA8\BISA/pro_bisa?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)

# 🗓 Función para formatear la fecha de los metadatos PDF
def formatear_fecha(fecha_pdf):
    if not fecha_pdf:
        return None
    try:
        fecha_limpia = fecha_pdf.replace("D:", "")[:8]
        fecha_obj = datetime.strptime(fecha_limpia, "%Y%m%d")
        return fecha_obj.strftime("%Y-%m-%d")
    except Exception:
        return None

# 📥 Extraer metadatos y guardarlos en la base de datos
def extraer_metadatos_y_guardar():
    with Session(engine) as session:
        for archivo in os.listdir(carpeta_pdfs):
            if archivo.lower().endswith(".pdf"):
                ruta_pdf = os.path.join(carpeta_pdfs, archivo)
                try:
                    with fitz.open(ruta_pdf) as doc:
                        metadata = doc.metadata
                        metadato = MetadatosPDF(
                            archivo=archivo,
                            titulo=metadata.get("title"),
                            autor=metadata.get("author"),
                            asunto=metadata.get("subject"),
                            palabras_clave=metadata.get("keywords"),
                            creador=metadata.get("creator"),
                            fecha_creacion=formatear_fecha(metadata.get("creationDate")),
                            fecha_modificacion=formatear_fecha(metadata.get("modDate")),
                            numero_paginas=doc.page_count
                        )
                        session.add(metadato)
                except Exception as e:
                    print(f"⚠️ Error al procesar {archivo}: {e}")
        session.commit()
        print("✅ Metadatos extraídos e insertados en la base de datos.")

# ▶️ Ejecutar solo si este script es llamado directamente
if __name__ == "__main__":
    extraer_metadatos_y_guardar()
