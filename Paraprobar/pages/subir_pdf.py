import reflex as rx
from ..backend.table_state import PdfState
from ..templates import template

@template(route="/subir-pdf", title="Subir PDF")
def subir_pdf() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir PDF", size="5"),
            rx.button(
                "REGRESAR",
                on_click=rx.redirect("/"),
                color_scheme="blue",
                variant="solid",
                size="2",
            ),
            spacing="9",
            align_items="center",
        ),
        rx.upload(
            rx.text("Arrastra y suelta tu PDF aquí o haz clic para seleccionar"),
            border="1px dashed #ccc",
            padding="4rem",
            id="pdf_upload",
        ),
        rx.button(
            "Procesar PDF",
            on_click=PdfState.handle_upload(rx.upload_files(upload_id="pdf_upload")),
        ),
        rx.text(PdfState.status),
        spacing="2",
        width="100%",
    )