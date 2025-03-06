from .pdf_processor import process_pdf
import reflex as rx
import os
from ultralytics import YOLO
import PyPDF2

# Cargar el modelo YOLO fuera de la clase TableState
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

    def handle_upload_pdf(self, files: list):
        print("Entró a handle_upload_pdf")
        if not files:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return

        file_data = files[0]
        temp_pdf_path = "temp_uploaded.pdf"
        with open(temp_pdf_path, "wb") as buffer:
            buffer.write(file_data)

        # Verificar si el archivo tiene páginas
        try:
            with open(temp_pdf_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                print(f"El archivo tiene {num_pages} páginas.")
                if num_pages == 0:
                    raise ValueError("El PDF no tiene páginas reconocibles.")
        except Exception as e:
            print(f"Error al leer el PDF: {e}")
            self.upload_success = False
            return

        # Procesar el PDF con YOLO
        try:
            result = process_pdf(temp_pdf_path, modelo_yolo)
            self.codigo_proyecto = result.get('Código de proyecto', '')
            self.disciplina = result.get('Disciplina', '')
            self.clasificacion_entregable = result.get('Clasificación de entregable', '')
            self.tipo_entregable = result.get('Tipo de entregable', '')
            self.codigo_entregable = result.get('Código de entregable', '')
            self.extracted_data = True
            self.upload_success = True
        except Exception as e:
            print(f"Error al procesar el PDF: {e}")
            self.upload_success = False
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

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