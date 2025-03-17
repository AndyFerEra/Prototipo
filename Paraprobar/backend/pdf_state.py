import reflex as rx
import os
from .pdf_processor import process_pdf
from ultralytics import YOLO
from typing import List
from ..repository.database import get_session
from ..models.entregable_model import Entregable

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
    total_hh: str = ""
    extracted_data: bool = False
    uploaded_file_path: str = ""
    uploaded_file: str = ""  # Nombre del archivo subido
    file_url: str = ""  # URL del archivo subido
    is_loading: bool = False  # Variable para controlar el spinner
    show_summary: bool = False
    show_alert_entregables: bool = False
    show_alert_hh: bool = False
    show_uploader: bool = True

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Maneja la subida de archivos y los guarda en la carpeta de uploads."""
        if not files:
            return rx.window_alert("No se seleccionó ningún archivo.")

        self.is_loading = True
        upload_dir = os.path.join("Paraprobar", "static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file in files:
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            self.uploaded_file = file.name
            self.file_url = f"/static/uploads/{file.name}"
            self.uploaded_file_path = file_path

        await self.handle_upload_pdf()

    async def handle_upload_pdf(self):
        """Procesa el archivo PDF subido y extrae la información."""
        if not self.uploaded_file_path:
            self.upload_success = False
            self.is_loading = False
            return

        try:
            result = process_pdf(self.uploaded_file_path, modelo_yolo)
            self.codigo_proyecto = result['Código de proyecto']
            self.disciplina = result['Disciplina']
            self.clasificacion_entregable = result['Clasificación de entregable']
            self.tipo_entregable = result['Tipo de entregable']
            self.codigo_entregable = result['Código de entregable']
            self.extracted_data = True
            self.upload_success = True
            self.show_uploader = False
        except Exception as e:
            print(f"Error al procesar el PDF: {e}")
            self.upload_success = False
        finally:
            self.is_loading = False

    def codigo_existe(self, codigo):
        """Verifica si el código del entregable ya existe en la base de datos."""
        with get_session() as session:
            return session.query(Entregable).filter_by(codigo_entregable=codigo).first() is not None

    def corregir_y_guardar(self):
        """Valida los datos y ajusta los estados para mostrar mensajes o el resumen."""
        # Reiniciar estados para evitar conflictos
        self.show_summary = False
        self.show_alert_entregables = False
        self.show_alert_hh = False

        # Validar si el código del entregable ya existe
        if self.codigo_existe(self.codigo_entregable):
            self.show_alert_entregables = True
            print("Error: El código del entregable ya existe.")
            return

        # Validar el campo Total HH como número válido
        try:
            self.total_hh = str(float(self.total_hh))  # Convertir a número válido
        except ValueError:
            self.show_alert_hh = True
            print("Error: El campo Total HH no es válido.")
            return

        # Si todo está bien, activar el estado para mostrar el resumen
        self.show_summary = True
        print("Validaciones completadas. Resumen activado.")

    def guardar_datos(self):
        """Inserta los datos en la base de datos."""
        with get_session() as session:
            entregable = Entregable(
                nombre_entregable=self.nombre_entregable,
                codigo_proyecto=self.codigo_proyecto,
                disciplina=self.disciplina,
                clasificacion_entregable=self.clasificacion_entregable,
                tipo_entregable=self.tipo_entregable,
                codigo_entregable=self.codigo_entregable,
                total_hh=float(self.total_hh),
            )
            session.add(entregable)
            session.commit()

        return rx.window_alert("Datos guardados exitosamente.")



    def reset_states(self):
        """Restablece los estados al valor inicial."""
        self.upload_success = False
        self.nombre_entregable = ""
        self.codigo_proyecto = ""
        self.disciplina = ""
        self.clasificacion_entregable = ""
        self.tipo_entregable = ""
        self.codigo_entregable = ""
        self.total_hh = ""
        self.extracted_data = False
        self.uploaded_file = ""
        self.file_url = ""
        self.is_loading = False  # Restablecer el spinner
        self.show_uploader = True
        print("Estados restablecidos.")