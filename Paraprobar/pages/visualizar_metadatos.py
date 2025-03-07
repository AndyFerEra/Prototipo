import reflex as rx
from Paraprobar.backend.table_state import PdfState  
from Paraprobar.templates import template  

@template(route="/visualizar-metadatos", title="Metadatos de PDFs")
def visualizar_metadatos() -> rx.Component:
    return rx.box(
        rx.heading("Metadatos de PDFs", size="5"),  # Usa 5 (o cualquier valor entre 1 y 9)
        rx.foreach(
            PdfState.metadata_list,
            lambda metadata: rx.card(
                rx.text(f"Título: {metadata['title']}"),
                rx.text(f"Autor: {metadata['author']}"),
                rx.text(f"Año: {metadata['year']}"),
                rx.text(f"Palabras clave: {', '.join(metadata['keywords']) if metadata['keywords'] else 'Ninguna'}",),
                width="100%",
            ),
        ),
        padding="2rem",
    )