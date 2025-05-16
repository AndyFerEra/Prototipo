from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import * 
from ..models import Proyectos
import reflex as rx

class ProyectosState(rx.State):
    """La clase State."""
    items: List[Proyectos] = []
        
    search_value: str = ""
    search_value_proyectos: str = ""
    
    sort_value: str = ""
    sort_value_proyectos: str = ""

    sort_reverse: bool = False
    sort_reverse_proyectos: bool = False

    total_items: int = 60 #59 rows
    offset: int = 0
    limit: int = 15  # Número de filas por página

    uploaded_file_name: str = ""
    upload_success: bool = False
    error_message: str = ""


    #Para las busquedas y ordenamiento para arreglar
    @rx.var(cache=True)
    def filtered_sorted_items_proyectos(self) -> List[Proyectos]:
        
        items = self.items 

        # Filtrar elementos basados en el valor de ordenación seleccionado
        if self.sort_value_proyectos:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value_proyectos)).lower(),
                reverse=self.sort_reverse_proyectos,
            )

        # Filtrar elementos basados en el valor de búsqueda
        if self.search_value_proyectos:
            search_value = self.search_value_proyectos.strip().lower()
            print(f"🔎 Buscando: {search_value}")
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "codigo_proyecto", #Codigo Pry
                        "cliente", #Cliente
                        "año", #Año
                        "nombre_proyecto", #Nombre Pry
                        "etapa_ing", #Etp Ing
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
    
        
    #tabla proyectos falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_proyectosA(self) -> list[Proyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_proyectos[start_index:end_index]


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

#cargar datos de bd de proyectos
    def load_entries_proyectos(self):
        """Carga los datos al cargar la página"""
        try:
            with Session(engine) as session:
                # Consulta base
                query = select(Proyectos)
                
                # Ejecutar la consulta y obtener los datos
                datos_db = session.exec(query).all()

                self.items = [
                    Proyectos(
                        codigo_proyecto=item.codigo_proyecto,
                        cliente=item.cliente,
                        nombre_proyecto=item.nombre_proyecto,
                        etapa_ing=item.etapa_ing,
                        año=item.año,
                        cantidad_entregables_cierre=item.cantidad_entregables_cierre,
                        venta_cierre=item.venta_cierre,
                        ratiohh_entrg_cierre=item.ratiohh_entrg_cierre,
                        ratiocosto_entrg_cierre=item.ratiocosto_entrg_cierre,
                    )
                    for item in datos_db
                ]
                self.items.sort(
                    key=lambda x: x.id if x.id is not None else -1,  # o float('inf')
                    reverse=self.sort_reverse_proyectos
                )
                self.total_items = len(self.items)
                #print(f"Se cargaron {self.total_items} registros desde la base de datos de proyectos.")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")     

    def toggle_sort_proyectos(self):
        self.sort_reverse_proyectos = not self.sort_reverse_proyectos
        self.load_entries_proyectos()

    def handle_upload_proyectos(self, files: list):
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
                required_columns = {"Código de proyecto", "Orden de trabajo (OT)", "Cliente", "Nombre de Proyecto", "Sector", 
                                    "Etapa de ingeniería", "País", "Año", "Estado", "Cantidad de entregables  - Propuesta", 
                                    "HH - Propuesta", "Presupuesto Costo directo", "Presupuesto Total (Sin descuento comercial)", 
                                    "Ratio HH / entregable - Propuesta", "Ratio Costo Directo / entregable - Propuesta", 
                                    "Margenes - Propuesta", "Cantidad de entregables - cierre", "HH - cierre", "Venta - cierre", 
                                    "Ratio HH / entregable - Cierre", "Ratio Costo / entregable - Cierre", "Margenes - Cierre"}
                if not required_columns.issubset(df.columns):
                    print("Error: El archivo no tiene las columnas esperadas para los proyectos.")
                    self.upload_success = False
                    return
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    print(f"Error: El archivo no tiene las columnas esperadas para los proyectos. Faltan las columnas: {', '.join(missing_columns)}")
                    self.upload_success = False
                    return
                

                # Guardar los datos en la base de datos
                with Session(engine) as session:
                    for _, row in df.iterrows():
                        data = Proyectos(
                            codigo_proyecto=row["Código de proyecto"],
                            orden_trabajo=row["Orden de trabajo (OT)"],
                            cliente=row["Cliente"],
                            nombre_proyecto=row["Nombre de Proyecto"],
                            sector=row["Sector"],
                            etapa_ing=row["Etapa de ingeniería"],
                            pais=row["País"],
                            año=row["Año"],
                            estado=row["Estado"],
                            cant_entrg_prop=row["Cantidad de entregables  - Propuesta"],
                            hh_propuesta=row["HH - Propuesta"],
                            presu_costo_directo=row["Presupuesto Costo directo"],
                            presu_total_sindescu=row["Presupuesto Total (Sin descuento comercial)"],
                            ratiohh_entrg_propuesta=row["Ratio HH / entregable - Propuesta"],
                            ratiocd_entreg_pro=row["Ratio Costo Directo / entregable - Propuesta"],
                            margenes_propuesta=row["Margenes - Propuesta"],
                            cantidad_entregables_cierre=row["Cantidad de entregables - cierre"],
                            hh_cierre=row["HH - cierre"],
                            venta_cierre=row["Venta - cierre"],
                            ratiohh_entrg_cierre=row["Ratio HH / entregable - Cierre"],
                            ratiocosto_entrg_cierre=row["Ratio Costo / entregable - Cierre"],
                            margenes_cierre=row["Margenes - Cierre"],
                        )
                        session.add(data)
                    session.commit()

                self.upload_success = True
                print("Datos guardados en la base de datos para proyectos.")
        except Exception as e:
            print("Error al procesar el archivo:", e)
            self.upload_success = False   

