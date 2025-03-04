import csv
from pathlib import Path
from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import select_all, engine      
from ..models import ExcelData  
from .pdf_processor import process_pdf
import reflex as rx
import os
from ultralytics import YOLO

class Item(rx.Base):
    """La clase Item."""

    pipeline: str
    status: str
    workflow: str
    timestamp: str
    duration: str

# Cargar el modelo YOLO fuera de la clase TableState
ruta_modelo = os.path.join(os.path.dirname(__file__), "modelos", "best.pt")
if not os.path.exists(ruta_modelo):
    raise FileNotFoundError(f"El archivo del modelo no existe en: {ruta_modelo}")
modelo_yolo = YOLO(ruta_modelo)

import os
from ultralytics import YOLO
import reflex as rx
from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import select_all, engine
from ..models import ExcelData
from .pdf_processor import process_pdf

# Cargar el modelo YOLO fuera de la clase TableState
ruta_modelo = os.path.join(os.path.dirname(__file__), "modelos", "best.pt")
if not os.path.exists(ruta_modelo):
    raise FileNotFoundError(f"El archivo del modelo no existe en: {ruta_modelo}")
modelo_yolo = YOLO(ruta_modelo)

class TableState(rx.State):
    # Variables de estado
    items: List[ExcelData] = []
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False
    total_items: int = 0
    offset: int = 0
    limit: int = 12  # Número de filas por página
    uploaded_file_name: str = ""
    upload_success: bool = False
    codigo_proyecto: str = ""
    disciplina: str = ""
    clasificacion_entregable: str = ""
    tipo_entregable: str = ""
    codigo_entregable: str = ""
    extracted_data: bool = False

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[Item]:
        items = self.items
        if self.sort_value:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value)).lower(),
                reverse=self.sort_reverse,
            )
        if self.search_value:
            search_value = self.search_value.lower()
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "pipeline",
                        "status",
                        "workflow",
                        "timestamp",
                        "duration",
                    ]
                )
            ]
        return items

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 0
        )

    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[ExcelData]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items[start_index:end_index]

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    def load_entries(self):
        try:
            datos_db = select_all()  # Obtiene los datos desde la base de datos
            print(f"Datos obtenidos: {datos_db}")  # Debugging
            self.items = [
                ExcelData(
                    id=item.id,
                    nombre=item.nombre,
                    edad=item.edad,
                    email=item.email,
                )
                for item in datos_db
            ]
            self.total_items = len(self.items)
            print(f"Se cargaron {self.total_items} registros desde la base de datos.")
        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def handle_upload_excel(self, files: list):
        """Maneja la subida de archivos Excel."""
        if not files:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return

        file_data = files[0]
        self.uploaded_file_name = "archivo_subido.xlsx"
        try:
            with io.BytesIO(file_data) as file_stream:
                df = pd.read_excel(file_stream)
                required_columns = {"Nombre", "Edad", "Email"}
                if not required_columns.issubset(df.columns):
                    print("Error: El archivo no tiene las columnas esperadas.")
                    self.upload_success = False
                    return
                with Session(engine) as session:
                    for _, row in df.iterrows():
                        data = ExcelData(
                            nombre=row["Nombre"],
                            edad=row["Edad"],
                            email=row["Email"]
                        )
                        session.add(data)
                    session.commit()
                self.upload_success = True
                print("Datos guardados en la base de datos.")
        except Exception as e:
            print("Error al procesar el archivo:", e)
            self.upload_success = False

    def handle_upload_pdf(self, files: list):
        """Maneja la subida de archivos PDF."""
        if not files:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return

        file_data = files[0]
        temp_pdf_path = "temp_uploaded.pdf"
        with open(temp_pdf_path, "wb") as buffer:
            buffer.write(file_data)

        try:
            # Usar el modelo YOLO global
            result = process_pdf(temp_pdf_path, modelo_yolo)
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
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    def corregir_valores(self):
        """Corrige los valores extraídos del PDF."""
        print("Valores corregidos:", {
            "Código de proyecto": self.codigo_proyecto,
            "Disciplina": self.disciplina,
            "Clasificación de entregable": self.clasificacion_entregable,
            "Tipo de entregable": self.tipo_entregable,
            "Código de entregable": self.codigo_entregable
        })