import reflex as rx

from ..backend.table_state import TableState
from ..templates import template
from ..views.table import file_upload

@template(route="/agregar", title="Agregar Datos")
def agregar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir un nuevo excel de datos", size="5"),
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
        file_upload(),
        spacing="2",
        width="100%",
    )
