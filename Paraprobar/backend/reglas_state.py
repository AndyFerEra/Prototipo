from typing import List
import pandas as pd
import io
from sqlmodel import Session, func, or_
from ..repository.database import * 
from ..models import Reglas
import reflex as rx


class ReglasState(rx.State):
    """La clase State."""
    items: List[Reglas] = []
        
    search_value: str = ""
    search_value_reglas: str = ""
    
    sort_value: str = ""
    sort_value_reglas: str = ""
    
    sort_reverse: bool = False
    sort_reverse_reglas: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 15  # Número de filas por página

    uploaded_file_name: str = ""
    upload_success: bool = False
    error_message: str = ""

    #Para las busquedas y ordenamiento para arreglar
    @rx.var(cache=True)
    def filtered_sorted_items_reglas(self) -> List[Reglas]:
        items = self.items  

        # Ordenar si hay un criterio seleccionado
        if self.sort_value_reglas:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value_reglas)).lower(),
                reverse=self.sort_reverse_reglas,
            )

        # Filtrar si hay un valor de búsqueda
        if self.search_value_reglas:
            search_value = self.search_value_reglas.strip().lower()
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "codigo_disciplina",  # Cod Disc
                        "disciplina", # Disciplina 
                        "sector", #Sector
                        "etapa_ingenieria",  # ETp Ing
                        "estado", #Estado
                        "codigo_ted", #Cod TED
                        "ted", #TED
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
    
    #tabla reglas falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_reglas(self) -> list[Reglas]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_reglas[start_index:end_index]

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def first_page(self):
        self.offset = 0
        
    def last_page(self):
        """Ir a la última página"""
        self.offset = (self.total_pages - 1) * self.limit

#cargar datos de bd de reglas
    def load_entries_reglas(self):
        """Carga los datos al cargar la página"""
        
        try:
            datos_db = select_all_reglas()  # Obtiene los datos desde la base de datos
            #print(f"Datos obtenidos de reglas: {datos_db}")  # Debugging

            self.items = [
                Reglas(
                    id=item.id,
                    codigo_disciplina=item.codigo_disciplina,
                    disciplina=item.disciplina,
                    tipo_entregable=item.tipo_entregable,
                    codigo_ted=item.codigo_ted,
                    ted=item.ted,
                    sector=item.sector,
                    etapa_ingenieria=item.etapa_ingenieria,
                    estado=item.estado,
                )
                for item in datos_db
            ]
            
            self.items.sort(key=lambda x: x.id, reverse=self.sort_reverse_reglas)

            self.total_items = len(self.items)
            #print(f"Se cargaron {self.total_items} datos de reglas.")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")     

    def toggle_sort_reglas(self):
        self.sort_reverse_reglas = not self.sort_reverse_reglas
        self.load_entries_reglas()

    def handle_upload_reglas(self, files: list):
        """Maneja la subida de archivos."""
        if not files:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return  # Salir de la función si no hay archivos

        file_data = files[0]  # Accedemos a los datos binarios del archivo
        self.uploaded_file_name = "archivo_subido.xlsx"  # Nombre genérico para el archivo

        try:
            with io.BytesIO(file_data) as file_stream:
                df = pd.read_excel(file_stream)
                # Eliminar espacios adicionales en los nombres de las columnas
                df.columns = df.columns.str.strip()
                df = df.fillna("")  # Rellenar valores nulos con cadena vacía
                # Validar que las columnas esperadas existen en el archivo
                required_columns = {"Perfiles","Disciplina","Código Disciplina","Tipo de entregable","Código de WBS","Código",
                                    "Tipo de entregables detallado","Sector","Etapa de ingeniería","Estado"}
                if not required_columns.issubset(df.columns):
                    print("Error: El archivo no tiene las columnas esperadas para las reglas.")
                    self.upload_success = False
                    return
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    print(f"Error: El archivo no tiene las columnas esperadas para las reglas. Faltan las columnas: {', '.join(missing_columns)}")
                    self.upload_success = False
                    return
                

                # Guardar los datos en la base de datos
                with Session(engine) as session:
                    for _, row in df.iterrows():
                        data = Reglas(
                            perfiles=row["Perfiles"],
                            codigo_disciplina=row["Código Disciplina"],
                            disciplina=row["Disciplina"],
                            tipo_entregable=row["Tipo de entregable"],
                            codigo_wbs=row["Código de WBS"],
                            codigo_ted=row["Código"],
                            ted=row["Tipo de entregables detallado"],
                            sector=row["Sector"],
                            etapa_ingenieria=row["Etapa de ingeniería"],
                            estado=row["Estado"],
                        )
                        session.add(data)
                    session.commit()

                self.upload_success = True
                print("Datos guardados en la base de datos para reglas.")
        except Exception as e:
            print("Error al procesar el archivo:", e)
            self.upload_success = False   
        
