import reflex as rx
import os
from ultralytics import YOLO
from typing import List
from ..repository.database import get_session
from ..backend.pdf_processor import process_pdf
from ..models.excel_data import Entregables
from .constans import map_disciplinas, map_clasificacion_entregable, map_tipo_entregable
from ..models.excel_data import Proyectos
from typing import Optional
import fitz  # PyMuPDF
import cv2
import easyocr
from elasticsearch import Elasticsearch

# Cargar el modelo YOLO
ruta_modelo = os.path.join(os.path.dirname(__file__), "modelos", "best.pt")
if not os.path.exists(ruta_modelo):
    raise FileNotFoundError(f"El archivo del modelo no existe en: {ruta_modelo}")
modelo_yolo = YOLO(ruta_modelo)

def normalizar_valor_con_mapeo(valor, mapeo):
    """
    Busca un valor en el mapeo y devuelve la clave correspondiente si hay coincidencia.
    Si no encuentra, retorna 'Seleccionar'.
    """
    valor_limpio = valor.strip().lower()
    for clave, variantes in mapeo.items():
        for variante in variantes:
            if variante.strip().lower() == valor_limpio:
                return clave
    return "Seleccionar"

## ELASTICSEARCH ##
# Configurar conexión a Elasticsearch (añade esto después de las importaciones)
es = Elasticsearch("http://localhost:9200")

def pdf_a_imagen(pdf_path, dpi=300):
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # Solo la primera página
        mat = fitz.Matrix(dpi / 180, dpi / 180)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        imagen_path = "temp_pagina.png"
        pix.save(imagen_path)
        return imagen_path
    except Exception as e:
        print(f"Error al convertir PDF a imagen: {e}")
        return None

def detectar_roi_y_extraer_texto(imagen_path, modelo_yolo):
    try:
        imagen = cv2.imread(imagen_path)
        resultados = modelo_yolo(imagen_path)
        
        for resultado in resultados:
            cajas = resultado.boxes.xyxy
            for caja in cajas:
                x1, y1, x2, y2 = map(int, caja)
                roi = imagen[y1:y2, x1:x2]
                roi_path = "temp_roi.png"
                cv2.imwrite(roi_path, roi)
                
                reader = easyocr.Reader(["es"])
                result = reader.readtext(roi_path)
                texto = " ".join([text for (_, text, _) in result])
                
                os.remove(roi_path)
                return texto
    except Exception as e:
        print(f"Error al procesar ROI: {e}")
        return None

def extract_text_by_page(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            pages.append({"pagina": page_num + 1, "texto": page_text})
        return pages
    except Exception as e:
        print(f"Error al extraer texto por página del PDF {pdf_path}: {e}")
        return None

def is_pdf_document(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        return len(text) > 100
    except Exception as e:
        print(f"Error al determinar el tipo de PDF: {e}")
        return False

def indexar_en_elasticsearch_por_pagina(pdf_path, tipo, codigo_entregable, disciplina, texto_por_pagina):
    for pagina_data in texto_por_pagina:
        pagina = pagina_data["pagina"]
        texto = pagina_data["texto"]

        doc = {
            "codigo_entregable": codigo_entregable,
            "disciplina": disciplina,
            "tipo": tipo,
            "pagina": pagina,
            "texto": texto,
            "ruta_pdf": pdf_path
        }

        doc_id = f"{codigo_entregable}_pagina_{pagina}"

        try:
            es.index(index="pdf_documents", id=doc_id, document=doc)
            print(f"Página {pagina} del documento {codigo_entregable} indexada correctamente.")
        except Exception as e:
            print(f"Error al indexar página {pagina} de {codigo_entregable}: {e}")

class TableStatePDF(rx.State):
    upload_success: bool = False
    nombre_entregable: str = ""
    codigo_proyecto: str = ""
    disciplina: str = ""
    clasificacion_entregable: str = ""
    tipo_entregable: str = ""
    codigo_entregable: str = ""
    total_hh: str = ""
    extracted_data: bool = False
    uploaded_file_path: str = ""
    uploaded_file: str = ""  # Nombre del archivo subido
    file_url: str = ""  # URL del archivo subido
    is_loading: bool = False  # Variable para controlar el spinner
    show_summary: bool = False
    show_alert_entregables: bool = False
    show_alert_hh: bool = False
    show_uploader: bool = True

    proyecto_valido: Optional[bool] = None  # None: No verificado, True: Existe, False
    uploaded_file_original: str = ""  # Nombre del archivo original subido
    file_url_original: str = ""  # URL del archivo original subido
    uploaded_file_path_original: str = ""  # Ruta del archivo original
    has_pdf: bool = False
    has_original: bool = False

    show_alert_pdf_exists: bool = False
    show_alert_original_exists: bool = False
    show_alert_missing_pdf: bool = False
    show_alert_missing_original: bool = False

    @rx.var
    def pdf_component(self) -> rx.Component:
        """Componente memoizado del visor PDF"""
        return rx.vstack(
            rx.hstack(
                rx.icon("circle_check", size=20, color="green", margin_top="0.1rem"),
                rx.text(f"Archivo subido: {self.uploaded_file}", color="#1e252b"),
            ),
            rx.html(
                f"""
                <div>
                    <iframe src="http://192.168.18.11:8002/static/uploads/{self.uploaded_file}" 
                            width="250%" 
                            height="500px" 
                            style="border: none;"
                            loading="lazy">
                    </iframe>
                </div>
                """,
                key=f"pdf-iframe-{self.uploaded_file}"  # Clave única para evitar re-renders
            ),
            spacing="2",
        )
    
    @rx.var
    def original_file_component(self) -> rx.Component:
        """Componente para mostrar información del archivo original"""
        return rx.vstack(
            rx.hstack(
                rx.icon("circle_check", size=20, color="green", margin_top="0.1rem"),
                rx.text(f"Archivo original subido: {self.uploaded_file_original}", color="#1e252b"),
            ),
            rx.box(
                rx.text(f"Tipo: {self.uploaded_file_original.split('.')[-1].upper()}"),
                border="1px solid #ccc",
                padding="1rem",
                border_radius="4px",
                width="100%",
                background="#f8f9fa"
            ),
            spacing="2",
        )

    def buscar_entregable_por_codigo(self, codigo: str):
        """Busca un entregable por su código y devuelve sus datos si existe"""
        with get_session() as session:
            entregable = session.query(Entregables).filter_by(codigo_entregable=codigo).first()
            if entregable:
                return {
                    "nombre_entregable": entregable.nombre_entregable,
                    "codigo_proyecto": entregable.codigo_proyecto_entregables,
                    "disciplina": entregable.disciplina_entregables,
                    "clasificacion_entregable": entregable.clasificacion_entregable,
                    "tipo_entregable": entregable.tipo_entregable_entre,
                    "total_hh": str(entregable.total_hh) if entregable.total_hh else "",
                }
            return None
        
    def set_codigo_entregable(self, codigo: str):
        """Establece el código de entregable y autocompleta los campos si existe"""
        self.codigo_entregable = codigo
        
        # Solo buscar si el código no está vacío
        if codigo.strip():
            entregable = self.buscar_entregable_por_codigo(codigo)
            if entregable:
                self.nombre_entregable = entregable["nombre_entregable"]
                self.codigo_proyecto = entregable["codigo_proyecto"]
                self.disciplina = entregable["disciplina"]
                self.clasificacion_entregable = entregable["clasificacion_entregable"]
                self.tipo_entregable = entregable["tipo_entregable"]
                self.total_hh = entregable["total_hh"]
                
                # Verificar también el proyecto
                self.verificar_proyecto(entregable["codigo_proyecto"])

    def verificar_proyecto(self, codigo_proyecto: str):
        """Verifica si el código del proyecto existe en la base de datos."""
        with get_session() as session:
            proyecto = session.query(Entregables).filter_by(codigo_proyecto_entregables=codigo_proyecto).first()
            self.proyecto_valido = proyecto is not None

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Maneja la subida de archivos con validación de tipos según lo que ya existe en BD"""
        print(f"Archivos recibidos: {[f.filename for f in files]}")
        
        if not files:
            return rx.window_alert("Debe subir al menos un archivo")
        
        self.is_loading = True
        upload_dir = os.path.join("Paraprobar", "static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        self.has_pdf = False
        self.has_original = False
        
        try:
            # Procesar archivos primero para determinar tipos
            for file in files:
                file_path = os.path.join(upload_dir, file.filename)
                print(f"Procesando archivo: {file.filename}")
                
                content = await file.read()
                if not content:
                    continue
                    
                with open(file_path, "wb") as f:
                    f.write(content)

                if file.filename.lower().endswith('.pdf'):
                    self.uploaded_file = file.filename
                    self.file_url = f"/static/uploads/{file.filename}"
                    self.uploaded_file_path = file_path
                    self.has_pdf = True
                else:
                    self.uploaded_file_original = file.filename
                    self.file_url_original = f"/static/uploads/{file.filename}"
                    self.uploaded_file_path_original = file_path
                    self.has_original = True

            # Verificar estado en BD
            existe, tiene_pdf, tiene_original = self.get_entregable_existente(self.codigo_entregable)

            # Configurar estados para mostrar el Alert Dialog adecuado
            self.show_alert_entregables = False
            self.show_alert_pdf_exists = False
            self.show_alert_original_exists = False
            self.show_alert_missing_pdf = False
            self.show_alert_missing_original = False

            # Validar según lo que ya existe
            if existe:
                # Caso 1: Ambos archivos ya existen
                if tiene_pdf and tiene_original:
                    self.show_alert_entregables = True
                    self.is_loading = False
                    return
                
                # Caso 2: Ya tiene PDF y estamos subiendo otro PDF
                if tiene_pdf and self.has_pdf:
                    self.show_alert_pdf_exists = True
                    self.is_loading = False
                    return
                
                # Caso 3: Ya tiene original y estamos subiendo otro original
                if tiene_original and self.has_original:
                    self.show_alert_original_exists = True
                    self.is_loading = False
                    return

                # Caso 4: Falta PDF pero estamos subiendo original
                if not tiene_pdf and self.has_original:
                    self.show_alert_missing_pdf = True
                    self.is_loading = False
                    return
                    
                # Caso 5: Falta original pero estamos subiendo PDF
                if not tiene_original and self.has_pdf:
                    self.show_alert_missing_original = True
                    self.is_loading = False
                    return

            # Si es un nuevo archivo o reemplazo válido, procesar
            if self.has_pdf:
                await self.handle_upload_pdf()
            else:
                # Mostrar formulario para archivos no PDF
                self.extracted_data = True
                self.upload_success = True
                self.show_uploader = False
                
        except Exception as e:
            print(f"Error en handle_upload: {str(e)}")
            self.is_loading = False
            return rx.window_alert(f"Error al procesar archivos: {str(e)}")
        finally:
            self.is_loading = False

    async def handle_upload_pdf(self):
        """Procesa el archivo PDF subido y extrae la información."""
        if not self.uploaded_file_path:
            self.upload_success = False
            self.is_loading = False
            return

        try:
            result = process_pdf(self.uploaded_file_path, modelo_yolo)
            self.codigo_proyecto = result['Código de proyecto']
            self.disciplina = normalizar_valor_con_mapeo(result.get('Disciplina', ""), map_disciplinas)
            self.clasificacion_entregable = normalizar_valor_con_mapeo(result.get('Clasificación de entregable', ""), map_clasificacion_entregable)
            self.tipo_entregable = normalizar_valor_con_mapeo(result.get('Tipo de entregable', ""), map_tipo_entregable)
            self.codigo_entregable = result['Código de entregable']
            self.extracted_data = True
            self.upload_success = True
            self.show_uploader = False
        except Exception as e:
            print(f"Error al procesar el PDF: {e}")
            self.upload_success = False
        finally:
            self.is_loading = False
    
    def get_entregable_existente(self, codigo: str) -> tuple[bool, bool, bool]:
        """Verifica si el código del entregable ya existe y el estado de sus enlaces"""
        with get_session() as session:
            entregable = session.query(Entregables).filter_by(codigo_entregable=codigo).first()
            if not entregable:
                return (False, False, False)
            
            tiene_pdf = bool(entregable.enlace_pdf)
            tiene_original = bool(entregable.enlace_nativo)
            return (True, tiene_pdf, tiene_original)
    
    def corregir_y_guardar(self):
        """Valida los datos y ajusta los estados para mostrar mensajes o el resumen."""
        # Reiniciar estados para evitar conflictos
        self.show_summary = False
        self.show_alert_entregables = False
        self.show_alert_hh = False

        # Validar el campo Total HH como número válido
        try:
            self.total_hh = str(float(self.total_hh))  # Convertir a número válido
        except ValueError:
            self.show_alert_hh = True
            print("Error: El campo Total HH no es válido.")
            return

        # Verificar estado del entregable existente
        existe, tiene_pdf, tiene_original = self.get_entregable_existente(self.codigo_entregable)
        
        if existe:
            # Caso 1: Ambos enlaces están llenos - NO PERMITIR
            if tiene_pdf and tiene_original:
                self.show_alert_entregables = True
                print("Error: El código del entregable ya existe con ambos archivos.")
                return
            
            # Caso 2: Falta PDF pero estamos subiendo un original
            if not tiene_pdf and self.has_original:
                self.show_alert_entregables = True
                print("Error: Solo puede subir PDF para este entregable existente.")
                return
            
            # Caso 3: Falta original pero estamos subiendo un PDF
            if not tiene_original and self.has_pdf:
                self.show_alert_entregables = True
                print("Error: Solo puede subir archivo original para este entregable existente.")
                return

        # Si todo está bien, activar el estado para mostrar el resumen
        self.show_summary = True
        print("Validaciones completadas. Resumen activado.")

    disciplina_map = {
        "Geotecnia": "00GEOTECNIA",
        "Concreto": "01CONCRETO",
        "Estructuras": "02ESTRUCTURAS",
        "Arquitectura": "03ARQUITECTURA",
        "Mecánica": "04MECANICA",
        "Tuberías": "05TUBERIAS",
        "Eléctrica": "06ELECTRICA",
        "Instrumentación": "07INSTRUMENTACION",
        "Procesos": "08PROCESOS",
        "General": "99GENERAL",
        "BIM": "35BIM",
        "Costos": "25COSTOS",
    }

    def guardar_datos(self):
        """Guarda los datos del entregable y mueve los archivos al directorio final"""
        # Validar que los campos requeridos estén completos
        if not all([self.codigo_proyecto, self.disciplina, self.nombre_entregable, self.codigo_entregable]):
            return rx.window_alert("Faltan datos necesarios para guardar el entregable")

        # Obtener disciplina modificada
        disciplina_modificado = self.disciplina_map.get(self.disciplina, "99GENERAL")

        # Construir la ruta final
        base_dir = r"F:\Users\Usuario\COBRA PERU S.A\Base_de_datos_Ingenieria - Documentos\General\BD Entregables"
        ruta_final = os.path.join(
            base_dir,
            self.codigo_proyecto,
            disciplina_modificado,
        )

        # Crear el directorio si no existe
        if not os.path.exists(ruta_final):
            os.makedirs(ruta_final)

        # Generar nombres basados en el código de entregable
        nombre_base = self.codigo_entregable.replace("/", "-")
        
        try:
            # Mover y renombrar archivos
            archivo_final_pdf = ""
            archivo_final_original = ""
            
            if self.has_pdf:
                extension_pdf = os.path.splitext(self.uploaded_file)[1] or ".pdf"
                archivo_final_pdf = os.path.join(ruta_final, f"{nombre_base}{extension_pdf}")
                os.rename(self.uploaded_file_path, archivo_final_pdf)
                print(f"PDF renombrado y movido a: {archivo_final_pdf}")
                
                # Procesar el PDF para Elasticsearch
                if is_pdf_document(archivo_final_pdf):
                    # Es un documento, extraer texto por páginas
                    texto_por_pagina = extract_text_by_page(archivo_final_pdf)
                    if texto_por_pagina:
                        indexar_en_elasticsearch_por_pagina(
                            archivo_final_pdf,
                            "documento",
                            self.codigo_entregable,
                            self.disciplina,
                            texto_por_pagina
                        )
                else:
                    # Es un plano, procesar con YOLO y OCR
                    imagen_path = pdf_a_imagen(archivo_final_pdf)
                    if imagen_path:
                        texto = detectar_roi_y_extraer_texto(imagen_path, modelo_yolo)
                        if texto:
                            indexar_en_elasticsearch_por_pagina(
                                archivo_final_pdf,
                                "plano",
                                self.codigo_entregable,
                                self.disciplina,
                                [{"pagina": 1, "texto": texto}]
                            )
                        os.remove(imagen_path)
            
            if self.has_original:
                extension_original = os.path.splitext(self.uploaded_file_original)[1]
                archivo_final_original = os.path.join(ruta_final, f"{nombre_base}{extension_original}")
                os.rename(self.uploaded_file_path_original, archivo_final_original)
                print(f"Archivo original renombrado y movido a: {archivo_final_original}")

            # Eliminar archivos temporales
            for temp_file in [self.uploaded_file_path, self.uploaded_file_path_original]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

            # Guardar en la base de datos
            with get_session() as session:
                entregable_existente = session.query(Entregables).filter_by(
                    codigo_entregable=self.codigo_entregable
                ).first()
                
                if entregable_existente:
                    # Actualizar solo los campos que faltan
                    if self.has_pdf and not entregable_existente.enlace_pdf:
                        entregable_existente.enlace_pdf = archivo_final_pdf
                    if self.has_original and not entregable_existente.enlace_nativo:
                        entregable_existente.enlace_nativo = archivo_final_original
                    
                    # Actualizar otros campos
                    entregable_existente.nombre_entregable = self.nombre_entregable
                    entregable_existente.total_hh = float(self.total_hh) if self.total_hh else None
                    entregable_existente.clasificacion_entregable = self.clasificacion_entregable
                    entregable_existente.tipo_entregable_entre = self.tipo_entregable
                else:
                    # Crear nuevo entregable
                    entregable = Entregables(
                        nombre_entregable=self.nombre_entregable,
                        codigo_proyecto_entregables=self.codigo_proyecto,
                        disciplina_entregables=self.disciplina,
                        clasificacion_entregable=self.clasificacion_entregable,
                        tipo_entregable_entre=self.tipo_entregable,
                        codigo_entregable=self.codigo_entregable,
                        total_hh=float(self.total_hh) if self.total_hh else None,
                        enlace_pdf=archivo_final_pdf if self.has_pdf else "",
                        enlace_nativo=archivo_final_original if self.has_original else "",
                    )
                    session.add(entregable)
                
                session.commit()

            # Mostrar alerta de éxito
            mensaje = "Entregable guardado correctamente:\n"
            if self.has_pdf:
                mensaje += f"PDF: {archivo_final_pdf}\n"
            if self.has_original:
                mensaje += f"Original: {archivo_final_original}"
            return rx.window_alert(mensaje)

        except Exception as e:
            print(f"Error al guardar: {e}")
            return rx.window_alert(f"Error al guardar: {str(e)}")
        
    def reset_states(self):
        """Restablece los estados al valor inicial."""
        self.upload_success = False
        self.nombre_entregable = ""
        self.codigo_proyecto = ""
        self.disciplina = ""
        self.clasificacion_entregable = ""
        self.tipo_entregable = ""
        self.codigo_entregable = ""
        self.total_hh = ""
        self.extracted_data = False
        self.uploaded_file = ""
        self.file_url = ""
        self.is_loading = False  # Restablecer el spinner
        self.show_uploader = True

        self.uploaded_file_original = ""
        self.file_url_original = ""
        self.has_original = False
        self.has_pdf = False
        print("Estados restablecidos.")