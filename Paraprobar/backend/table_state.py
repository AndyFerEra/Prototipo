import csv
import pandas as pd
import io
from sqlmodel import Session
from typing import List, Dict, Any
import reflex as rx

from ..repository.database import select_all, engine
from ..models import ExcelData
from ..repository.storage import save_uploaded_excel, get_file_list, EXCEL_DIR

class TableState(rx.State):
    """Estado para manejar tablas y archivos Excel."""

    items: List[ExcelData] = []
    excel_data: List[Dict[str, Any]] = []
    excel_columns: List[str] = []
    
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 12  

    uploaded_file_name: str = ""
    upload_success: bool = False
    current_excel_path: str = ""
    excel_files: list[dict] = []

    def on_load(self):
        """Cargar datos al iniciar."""
        self.load_entries()
        self.excel_files = get_file_list(EXCEL_DIR)

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[ExcelData]:
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
                    for attr in ["nombre", "edad", "email"]
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
        """Cargar entradas de la base de datos."""
        try:
            datos_db = select_all()
            
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
            
        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")        
            
    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de archivos Excel."""
        if not files:
            self.upload_success = False
            return
            
        file = files[0]
        try:
            content = await file.read()
            
            excel_path = save_uploaded_excel(content, file.filename)
            self.current_excel_path = excel_path
            self.uploaded_file_name = file.filename
            
            with io.BytesIO(content) as file_stream:
                df = pd.read_excel(file_stream)
                
                self.excel_columns = df.columns.tolist()
                self.excel_data = df.to_dict('records')
                
                if {"Nombre", "Edad", "Email"}.issubset(df.columns):
                    with Session(engine) as session:
                        for _, row in df.iterrows():
                            data = ExcelData(
                                nombre=row["Nombre"],
                                edad=row["Edad"],
                                email=row["Email"]
                            )
                            session.add(data)
                        session.commit()
                    
                    self.load_entries()  
            
            self.upload_success = True
            self.excel_files = get_file_list(EXCEL_DIR)
            
        except Exception as e:
            print(f"Error al procesar el archivo Excel: {e}")
            self.upload_success = False
    
    def view_excel(self, excel_path: str):
        """Establece el Excel actual para visualización"""
        self.current_excel_path = excel_path