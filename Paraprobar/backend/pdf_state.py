import reflex as rx
import io
from PyPDF2 import PdfReader
from collections import Counter
import re
from ..models.excel_data import PdfMetadata
from ..repository.storage import save_uploaded_pdf, get_file_list, PDF_DIR

class PdfState(rx.State):
    metadata_list: list[PdfMetadata] = []
    status: str = ""
    upload_success: bool = False
    current_pdf_path: str = ""
    pdf_files: list[dict] = []
    
    def on_load(self):
        """Cargar la lista de PDFs al inicio"""
        self.pdf_files = get_file_list(PDF_DIR)
    
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Procesa la subida de PDFs y los guarda para visualización"""
        if not files:
            self.status = "No se seleccionó ningún archivo"
            self.upload_success = False
            return
            
        for file in files:
            try:
                content = await file.read()
                
                pdf_path = save_uploaded_pdf(content, file.filename)
                self.current_pdf_path = pdf_path

                metadata = self.extract_pdf_metadata(content)
                self.metadata_list.append(PdfMetadata(**metadata))
                
                self.status = f"PDF {file.filename} procesado con éxito!"
                self.upload_success = True

                self.pdf_files = get_file_list(PDF_DIR)
            except Exception as e:
                self.status = f"Error procesando {file.filename}: {str(e)}"
                self.upload_success = False
    
    def extract_pdf_metadata(self, content: bytes) -> dict:
        """Extrae metadatos básicos del PDF"""
        try:
            pdf = PdfReader(io.BytesIO(content))
            metadata = pdf.metadata
            text = " ".join([page.extract_text() or "" for page in pdf.pages])
            
            words = re.findall(r'\b\w+\b', text.lower()) 
            common_words = ["el", "la", "los", "las", "un", "una", "y", "o", "de", "del", "a", "en", "con", "por", "para"]
            filtered_words = [word for word in words if word not in common_words and len(word) > 3]
            word_counts = {}
            for word in filtered_words:
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1
            
            keywords = []
            for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                keywords.append(word)
            
            return {
                "title": metadata.get("/Title", "Sin título") if metadata else "Sin título",
                "author": metadata.get("/Author", "Desconocido") if metadata else "Desconocido",
                "year": metadata.get("/CreationDate", "N/A")[:4] if metadata and metadata.get("/CreationDate") else "N/A",
                "keywords": keywords,
            }
        except Exception as e:
            print(f"Error al extraer metadatos: {e}")
            return {
                "title": "Error al procesar",
                "author": "Desconocido",
                "year": "N/A",
                "keywords": [],
            }
    
    def view_pdf(self, pdf_path: str):
        """Establece el PDF actual para visualización"""
        self.current_pdf_path = pdf_path