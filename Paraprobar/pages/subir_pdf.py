import reflex as rx
from backend.table_state import PdfState  

def subir_pdf_page():
    return rx.vstack(
        rx.upload(
            rx.text("Arrastra y suelta tu PDF aquí o haz clic para seleccionar"),
            border="1px dashed #ccc",
            padding="4rem",
        ),
        rx.button("Procesar PDF", on_click=PdfState.handle_upload),
        rx.text(PdfState.status),  
        spacing="2rem",
        padding="2rem",
    )