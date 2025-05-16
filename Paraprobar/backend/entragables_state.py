from elasticsearch import Elasticsearch
from typing import List
import pandas as pd
import io
from sqlmodel import Session, func, or_
from ..repository.database import * 
from ..models import Entregables,vistaentregablesproyectos
import time
import reflex as rx

es = Elasticsearch("http://localhost:9200")

class EntragablesState(rx.State):
    """La clase State."""
    items: List[Entregables] = []
    filtered_items: List[Entregables] = []
        
    search_value: str = ""
    search_value_entregables: str = ""
    
    sort_value_entregables: str = ""
    
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