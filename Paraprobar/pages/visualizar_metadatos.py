import reflex as rx
from backend.table_state import PdfState

def visualizar_metadatos_page():
    return rx.box(
        rx.heading("Metadatos de PDFs", size="lg"),
        rx.foreach(
            PdfState.metadata_list,
            lambda metadata: rx.card(
                rx.text(f"Título: {metadata['title']}"),
                rx.text(f"Autor: {metadata['author']}"),
                rx.text(f"Año: {metadata['year']}"),
                rx.text(f"Palabras clave: {', '.join(metadata['keywords'])}"),
                width="100%",
            ),
        ),
        padding="2rem",
    )