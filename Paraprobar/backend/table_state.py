import csv
from pathlib import Path
from typing import List
import pandas as pd
import io
from sqlmodel import Session
from ..repository.database import * 
from ..models import ExcelData,Reglas,Proyectos,Entregables
from ..models.entregable_model import Entregable
import time
import reflex as rx
from elasticsearch import Elasticsearch

# Agrega esto al inicio del archivo
es = Elasticsearch("http://localhost:9200")

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
    search_value_reglas: str = ""
    search_value_proyectos: str = ""
    search_value_entregables: str = ""
    
    sort_value: str = ""
    sort_value_reglas: str = ""
    sort_value_proyectos: str = ""
    sort_value_entregables: str = ""
    
    sort_reverse: bool = False
    sort_reverse_reglas: bool = False
    sort_reverse_proyectos: bool = False
    sort_reverse_entregables: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 15  # Número de filas por página

    uploaded_file_name: str = ""
    upload_success: bool = False
    error_message: str = ""

    pdf_matches: dict = {}  # Almacenará coincidencias en PDFs por código de entregable
    
    def search_in_elasticsearch(self, search_term: str):
        """Busca en Elasticsearch y guarda resultados"""
        with self:
            self.pdf_matches = {}  # Limpiar resultados anteriores
            
            if not search_term:
                return
                
            try:
                query = {
                    "query": {
                        "match": {
                            "texto": {
                                "query": search_term,
                                "operator": "and"
                            }
                        }
                    },
                    "_source": ["codigo_entregable", "pagina", "texto"],
                    "size": 1000  # Aumentar si hay muchos resultados
                }
                
                result = es.search(index="pdf_documents", body=query)
                
                for hit in result['hits']['hits']:
                    codigo = hit['_source']['codigo_entregable']
                    if codigo not in self.pdf_matches:
                        self.pdf_matches[codigo] = []
                    
                    texto = hit['_source']['texto']
                    term_lower = search_term.lower()
                    texto_lower = texto.lower()
                    inicio = texto_lower.find(term_lower)
                    
                    # Extraer fragmento de contexto
                    fragmento = texto[max(0, inicio-50):min(len(texto), inicio+len(term_lower)+50)] if inicio != -1 else ""
                    
                    self.pdf_matches[codigo].append({
                        "pagina": hit['_source']['pagina'],
                        "fragmento": fragmento.strip() if fragmento else ""
                    })
                    
            except Exception as e:
                print(f"Error en búsqueda Elasticsearch: {e}")

    def set_search_value_entregables(self, value: str):
        """Actualiza el valor de búsqueda y realiza la búsqueda"""
        self.search_value_entregables = value
        self.offset = 0  # Resetear a la primera página
        
        # Realizar búsqueda en Elasticsearch
        self.search_in_elasticsearch(value)
        
        # Recargar los entregables
        return self.load_entries_entregables()
    
    def reset_upload_state_entregables(self):
        """Restablece el estado de la subida de archivo y redirige."""
        self.upload_success = False
        self.uploaded_file_name = ""
        return rx.redirect("/") 

    #Para las busquedas y ordenamiento
    def set_search_value_entregables(self, value: str):
        """Actualiza el valor de búsqueda y recarga los datos"""
        self.search_value_entregables = value
        self.offset = 0  # Resetear a la primera página
        return self.load_entries_entregables()

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

        # Ordenar si hay un criterio seleccionado
        if self.sort_value_reglas:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value_reglas)).lower(),
                reverse=self.sort_reverse_reglas,
            )

        # Filtrar si hay un valor de búsqueda
        if self.search_value_reglas:
            search_value = self.search_value_reglas.lower()
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
                    ]
                )
            ]

        return items

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
            search_value = self.search_value_proyectos.lower()
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
    def filtered_sorted_items_entregables(self) -> List[Entregables]:
        
        items = self.items 

        # Filtrar elementos basados en el valor de ordenación seleccionado
        if self.sort_value_entregables:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value_entregables)).lower(),
                reverse=self.sort_reverse_entregables,
            )

        # Filtrar elementos basados en el valor de búsqueda
        if self.search_value_entregables:
            search_value = self.search_value_entregables.lower()
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "nombre_entregable", #Nombre Entrgbl
                        "codigo_entregable", #Codigo Entrgbl
                        "codigo_proyecto_entregables",#Codigo Pry
                        "disciplina_entregables", #Disciplina
                        "tipo_entregable_entre", #Tipo Entrgbl
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

    def next_page(self):
        """Avanzar a la siguiente página"""
        if (self.offset + self.limit) < self.total_items:
            self.offset += self.limit
            return self.load_entries_entregables()  # <-- Asegúrate de llamar a load_entries_entregables

    def prev_page(self):
        """Retroceder a la página anterior"""
        if self.offset > 0:
            self.offset -= self.limit
            return self.load_entries_entregables()  # <-- Asegúrate de llamar a load_entries_entregables

    def first_page(self):
        """Ir a la primera página"""
        self.offset = 0
        return self.load_entries_entregables()  # Faltaba este return

    def last_page(self):
        """Ir a la última página"""
        self.offset = (self.total_pages - 1) * self.limit
        return self.load_entries_entregables()  # Faltaba este return
            
    #para la lectura y subida de datos        
           
            
    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def handle_upload(self, files: list):
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
            
            self.items.sort(key=lambda x: x.id, reverse=self.sort_reverse_reglas)

            self.total_items = len(self.items)
            print(f"Se cargaron {self.total_items} datos de reglas.")

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
            self.items.sort(key=lambda x: x.id, reverse=self.sort_reverse_proyectos)
            self.total_items = len(self.items)
            print(f"Se cargaron {self.total_items} registros desde la base de datos de proyectos.")

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

 #=======================================================================================================            
            
#cargar datos de bd de entregables
    def load_entries_entregables(self):
        """Carga optimizada con paginación directa en SQL"""
        try:
            with Session(engine) as session:
                # Consulta base
                query = select(Entregables)
                
                # Si hay búsqueda y coincidencias en PDF, priorizar esos entregables
                if self.search_value_entregables and self.pdf_matches:
                    codigos_con_coincidencias = list(self.pdf_matches.keys())
                    query = query.where(Entregables.codigo_entregable.in_(codigos_con_coincidencias))
                
                # Aplicar filtro de búsqueda en columnas
                if self.search_value_entregables:
                    search = f"%{self.search_value_entregables.lower()}%"
                    query = query.where(
                        or_(
                            Entregables.nombre_entregable.ilike(search),
                            Entregables.codigo_entregable.ilike(search),
                            Entregables.clasificacion_entregable.ilike(search),
                            Entregables.codigo_proyecto_entregables.ilike(search),
                            Entregables.disciplina_entregables.ilike(search),
                            Entregables.tipo_entregable_entre.ilike(search)
                        )
                    )
                
                # Contar total de registros
                self.total_items = session.exec(
                    select(func.count()).select_from(query.subquery())
                ).one()
                
                # Aplicar ordenamiento
                if self.sort_value_entregables:
                    field = getattr(Entregables, self.sort_value_entregables)
                    direction = desc if self.sort_reverse_entregables else asc
                    query = query.order_by(direction(field))
                
                # Aplicar paginación
                query = query.offset(self.offset).limit(self.limit)
                self.items = session.exec(query).all()
                
        except Exception as e:
            print(f"Error al cargar entregables: {e}")
            self.items = []
            self.total_items = 0

    @rx.var
    def get_current_page_entregables(self) -> list[Entregables]:
        """Versión optimizada con caché"""
        return self.items

    def toggle_sort_entregables(self):
        self.sort_reverse_entregables = not self.sort_reverse_entregables
        self.load_entries_entregables()

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