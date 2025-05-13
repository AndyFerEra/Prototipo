from elasticsearch import Elasticsearch, AsyncElasticsearch
from pathlib import Path
from typing import List
import pandas as pd
import io
from sqlmodel import Session, func, or_
from ..repository.database import * 
from ..models import ExcelData,Reglas,Proyectos,Entregables,vistaentregablesproyectos
import time
import reflex as rx
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

class TableState(rx.State):
    """La clase State."""
    items: List[ExcelData] = []
    filtered_items: List[Entregables] = []
        
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
    
    filters: dict[str, str] = {}  # Diccionario para almacenar los filtros aplicados
        
    @rx.var(cache=False)
    def unique_codigo_proyectos_cod_pry(self) -> list[str]:
        valores = get_unique_values_by_column("codigo_proyecto_entregables") or []
        return ["Ninguno"] + valores
    
    @rx.var(cache=False)
    def unique_codigo_proyectos_cliente(self) -> list[str]:
        valores = get_unique_values_by_column("cliente") or []
        return ["Ninguno"] + valores
    
    @rx.var(cache=False)
    def unique_codigo_proyectos_nom_proy(self) -> list[str]:
        valores = get_unique_values_by_column("nombre_proyecto") or []
        return ["Ninguno"] + valores
    
    @rx.var(cache=False)
    def unique_codigo_proyectos_disciplina(self) -> list[str]:
        valores = get_unique_values_by_column("disciplina_entregables") or []
        return ["Ninguno"] + valores
    
    @rx.var(cache=False)
    def unique_codigo_proyectos_tip_entre(self) -> list[str]:
        valores = get_unique_values_by_column("tipo_entregable_entre") or []
        return ["Ninguno"] + valores

    def set_filter(self, column: str, value: str):
        """Actualiza el filtro y aplica cambios en los datos."""
        if value == "Ninguno":
            # Si el usuario selecciona "Ninguno", elimina el filtro para la columna especificada
            self.filters.pop(column, None)
        elif value:  # Solo filtra si el valor no está vacío
            self.filters[column] = value
        else:
            self.filters.pop(column, None)  # Elimina el filtro si está vacío

    def apply_filters(self):
        """Filtra los elementos según los filtros seleccionados."""
        if not self.filters:
            self.filtered_items = self.items  # Si no hay filtros, muestra todos los datos
            return
        
        self.filtered_items = [
            item for item in self.items
            if all(
                str(getattr(item, col, "")).startswith(val)  # Convierte a str para evitar errores
                for col, val in self.filters.items()
            )
        ]
    
    def apply_table_filters(self) -> None:
        """Aplica los filtros de la tabla sin afectar la paginación."""
        if not self.filters:
            self.filtered_sorted_items_entregables = self.items  # Mostrar todo si no hay filtros
            return

        self.filtered_sorted_items_entregables = [
            item for item in self.items
            if all(
                str(getattr(item, col, "")).lower().startswith(val.lower())  # 🔥 Filtra por coincidencias sin importar mayúsculas/minúsculas
                for col, val in self.filters.items()
            )
        ]
    
    def refresh(self):
        """Método para actualizar la tabla."""
        self.dirty += 1  # Esto forzará un refresco de la tabla
    # Estados para Elasticsearch
    elasticsearch_results: list[dict] = []
    elasticsearch_loading: bool = False
    elasticsearch_error: str = ""

    async def perform_search(self, search_term: str):
        
        """Realiza la búsqueda dinámica en Elasticsearch"""
        self.elasticsearch_loading = True
        self.elasticsearch_error = ""
        self.elasticsearch_results = []
        
        try:
            if not search_term.strip():
                self.elasticsearch_loading = False
                return

            if not es.ping():
                raise ConnectionError("No se puede conectar a Elasticsearch")

            query = {
                "query": {
                    "match": {
                        "texto": {
                            "query": search_term,
                            "operator": "and"
                        }
                    }
                },
                "highlight": {
                    "fields": {
                        "texto": {
                            "fragment_size": 150,
                            "number_of_fragments": 1,
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        }
                    }
                },
                "_source": ["codigo_entregable", "pagina", "texto", "ruta_pdf"],
                "size": 10
            }
            
            response = es.search(index="pdf_documents", body=query)
            hits = response['hits']['hits']
            
            results = []
            for hit in hits:
                source = hit['_source']
                highlight = hit.get('highlight', {}).get('texto', [''])[0]
                
                ruta_pdf = source.get('ruta_pdf', '')
                if ruta_pdf:
                    ruta_normalizada = ruta_pdf.replace('\\', '/')
                    # Aquí aplicamos el reemplazo del path
                    #NO TOCAR PRIMERA RUTA NORMALIZADA
                    ruta_normalizada = ruta_normalizada.replace(
                            f'D:/Users/Leo/COBRA PERU S.A/',
                            f''
                        )
                    #ESTO CAMBIAR
                    ruta_normalizada = ruta_normalizada.replace(
                            f'F:/Users/Usuario/COBRA PERU S.A',
                            f''
                        )
                    # Construir URL con parámetros de búsqueda
                    page_num = source.get('pagina', 1)
                    enlace = (
                        f"http://localhost:8011/{ruta_normalizada}"
                        f"#search={search_term}&page={page_num}"
                    )
                else:
                    enlace = "#"
                
                results.append({
                    "codigo": source.get('codigo_entregable', 'N/A'),
                    "pagina": str(source.get('pagina', 'N/A')),
                    "texto": source.get('texto', '')[:200] + '...',
                    "highlight": highlight,
                    "enlace": enlace,
                    "search_term": search_term,
                    "page_num": source.get('pagina', 1)
                })
            
            self.elasticsearch_results = results
            
        except Exception as e:
            self.elasticsearch_error = f"Error en búsqueda: {str(e)}"
        finally:
            self.elasticsearch_loading = False
    
    def reset_upload_state_entregables(self):
        """Restablece el estado de la subida de archivo y redirige."""
        self.upload_success = False
        self.uploaded_file_name = ""
        return rx.redirect("/") 

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

    @rx.var(cache=False, initial_value=[])
    def filtered_sorted_items_entregables(self) -> list[vistaentregablesproyectos]:
        """Aplica filtros, búsqueda y ordenación antes de paginar los datos."""
        data = lafeeeeeeeeeeeee()  # Asegúrate de que esta función trae todos los datos

        # Aplicar los filtros combo box / esto permite buscar por el combo box
        for column, value in self.filters.items():
            if column == "Cod Pry":
                data = [item for item in data if item.codigo_proyecto_entregables == value]
            elif column == "Disciplina":
                data = [item for item in data if item.disciplina_entregables == value]
            elif column == "Tipo Entrgbl":
                data = [item for item in data if item.tipo_entregable_entre == value]
            elif column == "Cliente":
                data = [item for item in data if item.cliente == value]
            elif column == "Proyecto":
                data = [item for item in data if item.nombre_proyecto == value]
            

        # Filtrar elementos basados en el valor de búsqueda
        if self.search_value_entregables:
            search_value = self.search_value_entregables.strip().lower()
            print(f"🔎 Buscando: {search_value}")
            data = [
                item
                for item in data
                if any(#Esto es para lo que nos permite buscar en el input de busqueda
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "codigo_entregable", # Codigo Pry
                        "nombre_entregable", # Nombre Entrgbl
                    ]
                )
            ]

        # Ordenar elementos basados en el valor de ordenación seleccionado
        if self.sort_value_entregables:
            data = sorted(
                data,
                key=lambda item: str(getattr(item, self.sort_value_entregables)).lower(),
                reverse=self.sort_reverse_entregables,
            )

        return data

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
        
    #tabla proyectos falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_proyectosA(self) -> list[Proyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_proyectos[start_index:end_index]

    #tabla entregables falta ver bien del todo 
    @rx.var(cache=True, initial_value=[])
    def get_current_page_entregables(self) -> list[vistaentregablesproyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items_entregables[start_index:end_index]

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
                self.items.sort(key=lambda x: x.id, reverse=self.sort_reverse_proyectos)
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

 #=======================================================================================================            
            
#cargar datos de bd de entregables
    def load_entries_entregables(self):
        """Carga optimizada con paginación directa en SQL"""
        try:
            with Session(engine) as session:
                # Consulta base
                query = select(vistaentregablesproyectos)
                
                # Si hay búsqueda y coincidencias en PDF, priorizar esos entregables
                if self.search_value_entregables and self.pdf_matches:
                    codigos_con_coincidencias = list(self.pdf_matches.keys())
                    query = query.where(vistaentregablesproyectos.codigo_entregable.in_(codigos_con_coincidencias))
                
                # Aplicar filtro de búsqueda en columnas
                if self.search_value_entregables:
                    search = f"%{self.search_value_entregables.lower()}%"
                    query = query.where(
                        or_(
                            vistaentregablesproyectos.codigo_proyecto_entregables.ilike(search),
                            vistaentregablesproyectos.cliente.ilike(search),
                            vistaentregablesproyectos.nombre_proyecto.ilike(search),
                            vistaentregablesproyectos.disciplina_entregables.ilike(search),
                            vistaentregablesproyectos.tipo_entregable_entre.ilike(search),
                            vistaentregablesproyectos.codigo_entregable.ilike(search),
                            vistaentregablesproyectos.nombre_entregable.ilike(search),
                            vistaentregablesproyectos.total_hh.ilike(search),
                            vistaentregablesproyectos.enlace_pdf.ilike(search),
                            vistaentregablesproyectos.enlace_nativo.ilike(search),
                        )
                    )
                
                # Contar total de registros
                self.total_items = session.exec(
                    select(func.count()).select_from(query.subquery())
                ).one()
                
                # Aplicar paginación
                """ query = query.offset(self.offset).limit(self.limit)
                self.items = session.exec(query).all() """
                
        except Exception as e:
            #print(f"Error al cargar entregables: {e}")
            self.items = []
            self.total_items = 0    

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