import csv
from pathlib import Path
from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import engine  
from ..models import ExcelData  

import reflex as rx

class Item(rx.Base):
    """La clase Item."""

    pipeline: str
    status: str
    workflow: str
    timestamp: str
    duration: str

class TableState(rx.State):
    """La clase State."""

    items: List[Item] = []

    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 12  # Número de filas por página

    uploaded_file_name: str = ""
    upload_success: bool = False

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[Item]:
        items = self.items

        # Filtrar elementos basados en el valor de ordenación seleccionado
        if self.sort_value:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value)).lower(),
                reverse=self.sort_reverse,
            )

        # Filtrar elementos basados en el valor de búsqueda
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
    def get_current_page(self) -> list[Item]:
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
        with Path("data.csv").open(encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.items = [Item(**row) for row in reader]
            self.total_items = len(self.items)

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def handle_upload(self, files: list):
        """Maneja la subida de archivos."""
        if files:
            # Los archivos subidos son objetos de tipo bytes
            file_data = files[0]  # Accedemos a los datos binarios del archivo
            self.uploaded_file_name = "archivo_subido.xlsx"  # Nombre genérico para el archivo

            # Leer el archivo Excel desde los datos binarios
            try:
                # Usamos io.BytesIO para manejar los datos binarios como un archivo
                with io.BytesIO(file_data) as file_stream:
                    df = pd.read_excel(file_stream)
                    print("Datos del Excel:", df)

                    # Guardar los datos en la base de datos
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
