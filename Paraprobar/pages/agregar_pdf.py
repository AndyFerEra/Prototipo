import reflex as rx
from ..templates import template
from ..views.pdf_box import file_upload_PDF
from ..backend.pdf_state import TableStatePDF

@template(route="/agregar_pdf", title="Agregar PDF")
def agregar_pdf() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir un nuevo PDF de datos", size="5"),
            rx.button(
                "Limpiar",
                rx.icon("eraser", size=20, color="white"),
                on_click=[
                    TableStatePDF.reset_states,
                    rx.redirect("/agregar_pdf"),
                ],
                color_scheme="blue",
                variant="solid",
                size="2",
                color="white",
                background_color="#e9004c",
            ),
            spacing="9",
            align_items="center",
            margin_bottom="1rem",
        ),
        file_upload_PDF(),
        spacing="2",
        width="100%",
    )