import reflex as rx
from ..backend.table_state import PdfState
from ..templates import template

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
                    len(metadata.keywords) > 0,
                    rx.text(
                        "Palabras clave: " + 
                        ", ".join([kw for kw in metadata.keywords])
                    ),
                    rx.text("Palabras clave: Ninguna"),
                ),
                width="100%",
                margin="0.5em",
            ),
        ),
        padding="2rem",
    )