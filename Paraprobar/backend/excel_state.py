import reflex as rx
from typing import Dict, List, Any, Optional
from ..repository.storage import save_uploaded_excel, read_excel_file

class ExcelState(rx.State):
    """Estado para manejar Excel con Handsontable."""
    
    excel_data: List[Dict[str, Any]] = []
    columns: List[str] = []
    file_path: str = ""
    upload_status: str = ""
    
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de archivos Excel."""
        if not files:
            self.upload_status = "No se seleccionó ningún archivo"
            return
            
        file = files[0]
        try:
            content = await file.read()
            self.file_path = save_uploaded_excel(content, file.filename)
            excel_data = read_excel_file(self.file_path)
            
            # Tomamos la primera hoja por defecto
            first_sheet = list(excel_data.values())[0]
            self.columns = first_sheet['columns']
            self.excel_data = first_sheet['data']
            
            self.upload_status = f"Archivo {file.filename} cargado correctamente"
                
        except Exception as e:
            self.upload_status = f"Error al procesar el archivo: {str(e)}"
            
    def create_new_sheet(self):
        """Crea una nueva hoja en blanco."""
        self.columns = ["Columna 1", "Columna 2", "Columna 3"]
        self.excel_data = [{"Columna 1": "", "Columna 2": "", "Columna 3": ""}]
        self.upload_status = "Nueva hoja creada"

    def reset_upload_state(self):
        """Reinicia el estado de subida."""
        self.upload_status = ""
        self.file_path = ""
        self.excel_data = {}