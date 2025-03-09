import reflex as rx
import os
from .pdf_processor import process_pdf
from ultralytics import YOLO
from typing import List

# Cargar el modelo YOLO
ruta_modelo = os.path.join(os.path.dirname(__file__), "modelos", "best.pt")
if not os.path.exists(ruta_modelo):
    raise FileNotFoundError(f"El archivo del modelo no existe en: {ruta_modelo}")
modelo_yolo = YOLO(ruta_modelo)

class TableStatePDF(rx.State):
    upload_success: bool = False
    nombre_entregable: str = ""
    codigo_proyecto: str = ""
    disciplina: str = ""
    clasificacion_entregable: str = ""
    tipo_entregable: str = ""
    codigo_entregable: str = ""
    extracted_data: bool = False
    uploaded_file_path: str = ""
    uploaded_file: str = ""  # Nombre del archivo subido
    file_url: str = ""  # URL del archivo subido

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Maneja la subida de archivos y los guarda en la carpeta de uploads."""
        if not files:
            return rx.window_alert("No se seleccionó ningún archivo.")

        # Define la ruta donde se guardará el archivo
        upload_dir = os.path.join("Paraprobar", "static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file in files:
            file_path = os.path.join(upload_dir, file.name)

            # Guarda el archivo en el servidor
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Actualiza el estado con el nombre del archivo subido y la URL
            self.uploaded_file = file.name
            self.file_url = f"/static/uploads/{file.name}"  # Ruta relativa desde static
            self.uploaded_file_path = file_path  # Guarda la ruta del archivo para procesarlo

            # Procesa el PDF automáticamente después de subirlo
        self.handle_upload_pdf()

    def handle_upload_pdf(self):
        """Procesa el archivo PDF subido y extrae la información."""
        if not self.uploaded_file_path:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return

        try:
            # Procesar el PDF con el modelo YOLO
            result = process_pdf(self.uploaded_file_path, modelo_yolo)
            self.codigo_proyecto = result['Código de proyecto']
            self.disciplina = result['Disciplina']
            self.clasificacion_entregable = result['Clasificación de entregable']
            self.tipo_entregable = result['Tipo de entregable']
            self.codigo_entregable = result['Código de entregable']
            self.extracted_data = True
            self.upload_success = True
        except Exception as e:
            print(f"Error al procesar el PDF: {e}")
            self.upload_success = False

    def reset_states(self):
        """Restablece los estados al valor inicial."""
        self.upload_success = False
        self.nombre_entregable = ""
        self.codigo_proyecto = ""
        self.disciplina = ""
        self.clasificacion_entregable = ""
        self.tipo_entregable = ""
        self.codigo_entregable = ""
        self.extracted_data = False
        self.uploaded_file = ""
        self.file_url = ""
        print("Estados restablecidos.")

    def corregir_valores(self):
        """Corrige los valores extraídos del PDF."""
        print("Valores corregidos:", {
            "Nombre del entregable": self.nombre_entregable,
            "Código de proyecto": self.codigo_proyecto,
            "Disciplina": self.disciplina,
            "Clasificación de entregable": self.clasificacion_entregable,
            "Tipo de entregable": self.tipo_entregable,
            "Código de entregable": self.codigo_entregable
        })