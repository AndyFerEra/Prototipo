import csv
from pathlib import Path
from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import * 
from ..models import ExcelData,Reglas,Proyectos,Entregables	
import time
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

    items: List[ExcelData] = []
    
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 20  # Número de filas por página

    uploaded_file_name: str = ""
    upload_success: bool = False
    error_message: str = ""
    
    
    def reset_upload_state_entregables(self):
        """Restablece el estado de la subida de archivo y redirige."""
        self.upload_success = False
        self.uploaded_file_name = ""
        return rx.redirect("/") 

    #Para las busquedas y ordenamiento
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

    #Para las busquedas y ordenamiento para arreglar
    @rx.var(cache=True)
    def filtered_sorted_items_reglas(self) -> List[Reglas]:
        
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
                        "Cod Disc",
                        "Disciplina",
                        "Sector",
                        "Etp Ing",
                        "Estado",
                    ]
                )
            ]

        return items

    #Para las busquedas y ordenamiento para arreglar
    @rx.var(cache=True)
    def filtered_sorted_items_proyectos(self) -> List[Proyectos]:
        
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
                        "Cod Disc",
                        "Disciplina",
                        "Sector",
                        "Etp Ing",
                        "Estado",
                    ]
                )
            ]

        return items

    @rx.var(cache=True)
    def filtered_sorted_items_entregables(self) -> List[Entregables]:
        
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
                        "Cod Disc",
                        "Disciplina",
                        "Sector",
                        "Etp Ing",
                        "Estado",
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

    #tabla prueba
    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[ExcelData]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items[start_index:end_index]
    
    #tabla reglas falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_reglas(self) -> list[Reglas]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_reglas[start_index:end_index]
    
    #tabla proyectos falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_proyectos(self) -> list[Proyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_proyectos[start_index:end_index]

    #tabla entregables falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_entregables(self) -> list[Entregables]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_entregables[start_index:end_index]

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
            
    #para la lectura y subida de datos        
            
    #cargar datos de bd de prueba
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

    """ def handle_upload(self, files: list):
        # Maneja la subida de archivos.
        if not files:
            print("No se subió ningún archivo.")
            self.upload_success = False
            return  # Salir de la función si no hay archivos

        file_data = files[0]  # Accedemos a los datos binarios del archivo
        self.uploaded_file_name = "archivo_subido.xlsx"  # Nombre genérico para el archivo

        try:
            with io.BytesIO(file_data) as file_stream:
                df = pd.read_excel(file_stream)
                # Validar que las columnas esperadas existen en el archivo
                required_columns = {"Nombre", "Edad", "Email"}
                if not required_columns.issubset(df.columns):
                    print("Error: El archivo no tiene las columnas esperadas.")
                    self.upload_success = False
                    return

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
            """
 #=======================================================================================================            
            
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

            self.total_items = len(self.items)
            print(f"Se cargaron {self.total_items} datos de reglas.")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")     

    def toggle_sort_reglas(self):
        self.sort_reverse = not self.sort_reverse
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
        
 #=======================================================================================================            
            
 #cargar datos de bd de proyectos
    def load_entries_proyectos(self):
        """Carga los datos al cargar la página"""
        
        try:
            datos_db = select_all_proyectos()  # Obtiene los datos desde la base de datos
            #print(f"Datos obtenidos de proyectos: {datos_db}")  # Debugging

            self.items = [
                Proyectos(
                    id=item.id,
                    codigo_proyecto=item.codigo_proyecto,
                    orden_trabajo=item.orden_trabajo,
                    cliente=item.cliente,
                    nombre_proyecto=item.nombre_proyecto,
                    sector=item.sector,
                    etapa_ing=item.etapa_ing,
                    pais=item.pais,
                    año=item.año,
                    estado=item.estado,
                    cant_entrg_prop=item.cant_entrg_prop,
                    hh_propuesta=item.hh_propuesta,
                    presu_costo_directo=item.presu_costo_directo,
                    presu_total_sindescu=item.presu_total_sindescu,
                    ratiohh_entrg_propuesta=item.ratiohh_entrg_propuesta,
                    ratiocd_entreg_pro=item.ratiocd_entreg_pro,
                    margenes_propuesta=item.margenes_propuesta,
                    cantidad_entregables_cierre=item.cantidad_entregables_cierre,
                    hh_cierre=item.hh_cierre,
                    venta_cierre=item.venta_cierre,
                    ratiohh_entrg_cierre=item.ratiohh_entrg_cierre,
                    ratiocosto_entrg_cierre=item.ratiocosto_entrg_cierre,
                    margenes_cierre=item.margenes_cierre,
                )
                for item in datos_db
            ]

            self.total_items = len(self.items)
            print(f"Se cargaron {self.total_items} registros desde la base de datos de proyectos.")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")     

    def toggle_sort_proyectos(self):
        self.sort_reverse = not self.sort_reverse
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

 #=======================================================================================================            
            
#cargar datos de bd de entregables
    def load_entries_entregables(self):
        try:
            start_time = time.time()  # Iniciar cronómetro

            datos_db = select_all_entregables_2()  # Obtiene los datos desde la base de datos
            db_time = time.time()  # Tiempo después de obtener los datos

            self.items = [
                Entregables(
                    id=item.id,
                    codigo_proyecto_entregables=item.codigo_proyecto_entregables,
                    disciplina_entregables=item.disciplina_entregables,
                    clasificacion_entregable=item.clasificacion_entregable,
                    tipo_entregable_entre=item.tipo_entregable_entre,
                    codigo_entregable=item.codigo_entregable,
                    nombre_entregable=item.nombre_entregable,
                    total_hh=item.total_hh,
                    enlace_pdf=item.enlace_pdf,
                    enlace_nativo=item.enlace_nativo,
                )
                for item in datos_db
            ]

            process_time = time.time()  # Tiempo después de procesar los datos

            self.total_items = len(self.items)
            print(f"✅ Se cargaron {self.total_items} datos de entregables.")
            print(f"⏱ Tiempo de consulta a BD/Caché: {db_time - start_time:.4f} s")
            print(f"⏳ Tiempo de procesamiento de datos: {process_time - db_time:.4f} s")
            print(f"🚀 Tiempo total: {process_time - start_time:.4f} s")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")    

    def toggle_sort_entregables(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries_entregables()

    """ def handle_upload_entregables(self, files: list):
        #Maneja la subida de archivos.
        print("handle_upload_entregables ha sido llamado")
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
                required_columns = {"ID", "Código de proyecto", "Disciplina", "Clasificación de entregable", "Tipo de entregable", 
                                    "Código de entregable", "Nombre de entregable", "Total HH", "Enlace al entregable (PDF)", 
                                    "Enlace al entregable (Nativo)"}
                if not required_columns.issubset(df.columns):
                    print("Error: El archivo no tiene las columnas esperadas para los entregables.")
                    self.upload_success = False
                    return
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    print(f"Error: El archivo no tiene las columnas esperadas para los entregables. Faltan las columnas: {', '.join(missing_columns)}")
                    self.upload_success = False
                    return
                
                start_time = time.time()
                # Guardar los datos en la base de datos
                with Session(engine) as session:
                    for _, row in df.iterrows():
                        data = Entregables(
                            codigo_proyecto_entregables=row["Código de proyecto"],
                            disciplina_entregables=row["Disciplina"],
                            clasificacion_entregable=row["Clasificación de entregable"],
                            tipo_entregable_entre=row["Tipo de entregable"],
                            codigo_entregable=row["Código de entregable"],
                            nombre_entregable=row["Nombre de entregable"],
                            total_hh=row["Total HH"],
                            enlace_pdf=row["Enlace al entregable (PDF)"],
                            enlace_nativo=row["Enlace al entregable (Nativo)"],
                        )
                        session.add(data)
                    session.commit()

                end_time = time.time()
                print(f"Tiempo total de inserción: {end_time - start_time:.2f} segundos")
                self.upload_success = True
                print("Datos guardados en la base de datos para entregables.")
        except Exception as e:
            print("Error al procesar el archivo:", e)
            self.upload_success = False  """

    def handle_upload_entregables(self, files: list):
        try:
            rx.console_log(f"Archivo recibido: {self.uploaded_file_name}" if files else "No se subió ningún archivo")

            """Maneja la subida de archivos."""
            print("handle_upload_entregables ha sido llamado")
            
            if not files:
                print("No se subió ningún archivo.")
                self.upload_success = False
                return

            file_data = files[0]  
            self.uploaded_file_name = "archivo_subido.xlsx"  

            try:
                with io.BytesIO(file_data) as file_stream:
                    df = pd.read_excel(file_stream)

                # Limpiar nombres de columnas y rellenar valores nulos
                df.columns = df.columns.str.strip()
                df = df.fillna("")

                # Validar que las columnas esperadas existen
                required_columns = {
                    "Código de proyecto", "Disciplina", "Clasificación de entregable", "Tipo de entregable",
                    "Código de entregable", "Nombre de entregable", "Total HH", "Enlace al entregable (PDF)",
                    "Enlace al entregable (Nativo)"
                }

                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    print(f"Error: Faltan las siguientes columnas en el archivo: {', '.join(missing_columns)}")
                    self.upload_success = False
                    return

                # Limpiar datos problemáticos
                df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)  # Elimina espacios en blanco
                df.replace({None: ""}, inplace=True)  # Evita valores None
                df["Nombre de entregable"] = df["Nombre de entregable"].str.slice(0, 255)  # Limita longitud si es necesario

                # Convertir DataFrame en lista de diccionarios para bulk_insert
                data_to_insert = df.rename(columns={
                    "Código de proyecto": "codigo_proyecto_entregables",
                    "Disciplina": "disciplina_entregables",
                    "Clasificación de entregable": "clasificacion_entregable",
                    "Tipo de entregable": "tipo_entregable_entre",
                    "Código de entregable": "codigo_entregable",
                    "Nombre de entregable": "nombre_entregable",
                    "Total HH": "total_hh",
                    "Enlace al entregable (PDF)": "enlace_pdf",
                    "Enlace al entregable (Nativo)": "enlace_nativo"
                }).to_dict(orient="records")

                start_time = time.time()
                batch_size = 100  # Inserta en lotes de 100 registros

                with Session(engine) as session:
                    for i in range(0, len(data_to_insert), batch_size):
                        #print(f"Insertando registros {i} a {i+batch_size}...")  # Depuración
                        session.bulk_insert_mappings(Entregables, data_to_insert[i:i+batch_size])
                        session.commit()

                end_time = time.time()
                print(f"Tiempo total de inserción: {end_time - start_time:.2f} segundos")

                self.upload_success = True
                print("Datos guardados en la base de datos para entregables.")

            except Exception as e:
                print("Error al procesar el archivo:", e)
                self.upload_success = False
        except Exception as e:
            print(f"Error en handle_upload_entregables: {e}")
            self.upload_success = False