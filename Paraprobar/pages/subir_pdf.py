import reflex as rx
from ..backend.pdf_state import PdfState  
from ..templates import template
from ..views.pdf_viewer import pdf_viewer, pdf_file_list

from reflex.components.core.breakpoints import Breakpoints

@template(route="/subir-pdf", title="Subir PDF", on_load=PdfState.on_load)
def subir_pdf() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir y Visualizar PDFs", size="5"),
            rx.button(
                "REGRESAR",
                on_click=rx.redirect("/"),  
                color_scheme="blue",
                variant="solid",
                size="2", 
            ),
            spacing="9",  
            align_items="center",
            width="100%",
        ),
        
        rx.card(
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.icon("file_archive", size=40, color="blue"),
                        rx.text("Arrastra y suelta tu PDF aquí o haz clic para seleccionar"),
                    ),
                    border="1px dashed #ccc",
                    padding="2rem",
                    border_radius="md",
                    id="pdf_upload",
                    accept={"application/pdf": [".pdf"]},
                    max_files=1,
                ),
                rx.button(
                    "Procesar PDF",
                    on_click=PdfState.handle_upload(rx.upload_files(upload_id="pdf_upload")),
                    color_scheme="blue",
                    variant="solid",
                    margin_top="1em",
                ),
                rx.cond(
                    PdfState.upload_success,
                    rx.text(PdfState.status, color="green"),
                    rx.text(PdfState.status, color="red"),
                ),
                spacing="2",
                width="100%",
                align_items="center",
                padding="1em",
            ),
            width="100%",
        ),

        rx.flex(
            rx.box(
                pdf_file_list(PdfState.pdf_files, on_select=PdfState.view_pdf),
                width="30%",
                padding="1em",
            ),

            rx.box(
                rx.cond(
                    PdfState.current_pdf_path,
                    pdf_viewer(PdfState.current_pdf_path),
                    rx.text("Seleccione un PDF para visualizar", padding="2em", text_align="center"),
                ),
                width="70%",
                padding="1em",
            ),
            width="100%",
            direction=Breakpoints(base='column', md='column', lg='row'),
            spacing="4",
        ),
        

        rx.cond(
            PdfState.upload_success,
            rx.button(
                "Ver Metadatos",
                on_click=rx.redirect("/visualizar-metadatos"),
                color_scheme="green",
                variant="solid",
                margin_top="1em",
            ),
            rx.text(""),
        ),
        
        spacing="4",
        width="100%",
        padding="1em",
    )