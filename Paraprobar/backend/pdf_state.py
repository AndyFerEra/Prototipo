import reflex as rx
import os
from ultralytics import YOLO
from typing import List
from ..repository.database import get_session
from ..models.entregable_model import Entregable
from .constans import map_disciplinas, map_clasificacion_entregable, map_tipo_entregable
from ..models.excel_data import Proyectos
from typing import Optional

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

    def verificar_proyecto(self, codigo_proyecto: str):
        """Verifica si el código del proyecto existe en la base de datos."""
        with get_session() as session:
            proyecto = session.query(Proyectos).filter_by(codigo_proyecto=codigo_proyecto).first()
            self.proyecto_valido = proyecto is not None

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Maneja la subida de archivos y los guarda en la carpeta de uploads."""
        if not files:
            return rx.window_alert("No se seleccionó ningún archivo.")

        self.is_loading = True
        upload_dir = os.path.join("Paraprobar", "static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file in files:
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            self.uploaded_file = file.name
            self.file_url = f"/static/uploads/{file.name}"
            self.uploaded_file_path = file_path
        
        self.extracted_data = True

    def codigo_existe(self, codigo):
        """Verifica si el código del entregable ya existe en la base de datos."""
        with get_session() as session:
            return session.query(Entregable).filter_by(codigo_entregable=codigo).first() is not None

    def corregir_y_guardar(self):
        """Valida los datos y ajusta los estados para mostrar mensajes o el resumen."""
        # Reiniciar estados para evitar conflictos
        self.show_summary = False
        self.show_alert_entregables = False
        self.show_alert_hh = False

        # Validar si el código del entregable ya existe
        if self.codigo_existe(self.codigo_entregable):
            self.show_alert_entregables = True
            print("Error: El código del entregable ya existe.")
            return

        # Validar el campo Total HH como número válido
        try:
            self.total_hh = str(float(self.total_hh))  # Convertir a número válido
        except ValueError:
            self.show_alert_hh = True
            print("Error: El campo Total HH no es válido.")
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
        """Guarda los datos del entregable y mueve el PDF al directorio final."""
        # Validar que los campos requeridos estén completos
        if not all([self.codigo_proyecto, self.disciplina, self.nombre_entregable, self.uploaded_file_path]):
            return rx.window_alert("Faltan datos necesarios para guardar el entregable.")

        # Obtener disciplina modificada
        disciplina_modificado = self.disciplina_map.get(self.disciplina, "99GENERAL")

        # Construir la ruta final
        base_dir = r"C:\Users\Leo\COBRA PERU S.A\Base_de_datos_Ingenieria - Documentos\General\BD Entregables"
        ruta_final = os.path.join(
            base_dir,
            self.codigo_proyecto,
            disciplina_modificado,
        )

        # Crear el directorio si no existe
        if not os.path.exists(ruta_final):
            os.makedirs(ruta_final)

        # Ruta completa del archivo final
        archivo_final = os.path.join(ruta_final, f"{self.nombre_entregable}.pdf")

        try:
            # Mover el archivo desde la carpeta temporal a la ruta final
            os.rename(self.uploaded_file_path, archivo_final)
            print(f"Archivo movido exitosamente a: {archivo_final}")

            # Eliminar el archivo temporal en /static/uploads
            if os.path.exists(self.uploaded_file_path):
                os.remove(self.uploaded_file_path)
                print(f"Archivo temporal eliminado: {self.uploaded_file_path}")

            # Guardar los datos en la base de datos
            with get_session() as session:
                entregable = Entregable(
                    nombre_entregable=self.nombre_entregable,
                    codigo_proyecto=self.codigo_proyecto,
                    disciplina=self.disciplina,
                    clasificacion_entregable=self.clasificacion_entregable,
                    tipo_entregable=self.tipo_entregable,
                    codigo_entregable=self.codigo_entregable,
                    total_hh=float(self.total_hh) if self.total_hh else None,
                )
                session.add(entregable)
                session.commit()

            # Mostrar alerta de éxito
            return rx.window_alert(f"El entregable ha sido guardado correctamente en:\n{archivo_final}")

        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            return rx.window_alert("Error al guardar el entregable. Revisa la consola para más información.")



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
        print("Estados restablecidos.")