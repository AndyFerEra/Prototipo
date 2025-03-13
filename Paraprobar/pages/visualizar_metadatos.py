import reflex as rx
from Paraprobar.backend.table_state import PdfState  
from Paraprobar.templates import template  

@template(route="/visualizar-metadatos", title="Metadatos de PDFs")
def visualizar_metadatos() -> rx.Component:
    return rx.box(
        rx.heading("Metadatos de PDFs", size="5"),
        rx.foreach(
            PdfState.metadata_list,
            lambda metadata: rx.card(
                rx.text(f"Título: {metadata.title}"),
                rx.text(f"Autor: {metadata.author}"),
                rx.text(f"Año: {metadata.year}"),
                rx.cond(
                    metadata.keywords,
                    rx.text(
                        "Palabras clave: " + ", ".join(metadata.keywords),
                    ),
                    rx.text("Palabras clave: Ninguna"),
                ),
                width="100%",
            ),
        ),
        padding="2rem",
    )