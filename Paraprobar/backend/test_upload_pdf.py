import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.pdf_state import TableStatePDF

ruta_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "MPDX03-EI23062_66_78-P159CON-110-DW-A-001_1.pdf"))

def probar_carga_pdf():
    """Simula la carga de un archivo PDF sin usar Reflex."""
    try:
        with open(ruta_pdf, "rb") as file:
            pdf_data = file.read() 

        # Crear un objeto temporal con solo la función que queremos probar
        class MockTableStatePDF:
            def handle_upload_pdf(self, files):
                print("Entró a handle_upload_pdf")
                TableStatePDF.handle_upload_pdf(self, files)

        # Simular la carga del PDF
        estado_pdf = MockTableStatePDF()
        estado_pdf.handle_upload_pdf([pdf_data])

        print("Prueba completada exitosamente")

    except Exception as e:
        print("Error al probar la carga de PDF:", e)

# Ejecutar la prueba
if __name__ == "__main__":
    probar_carga_pdf()

