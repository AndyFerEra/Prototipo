import reflex as rx
from ..backend.pdf_state import PdfState
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
                rx.box(
                    rx.text("Palabras clave: "),
                    rx.foreach(
                        metadata.keywords,
                        lambda kw: rx.text(f"{kw}, ", inline=True)
                    ),
                ),
                width="100%",
                margin="0.5em",
            ),
        ),
        padding="2rem",
    )