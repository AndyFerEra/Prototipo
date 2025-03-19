import reflex as rx

from ..backend.table_state import TableState
from ..templates import template
from ..views.table_reglas import file_upload_reglas
from ..views.table_proyectos import file_upload_proyectos
from ..views.table_entregables_2 import file_upload_entregables

try:
    @template(route="/agregarEntregables", title="Agregar Entregables")
    def agregarEntregables() -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading("Subir el excel de datos para los entregables", size="5"),
                rx.button(
                    "REGRESAR",
                    on_click=TableState.reset_upload_state_entregables,
                    color_scheme="blue",
                    variant="solid",
                    size="2", 
                ),
                spacing="9",  
                align_items="center",
            ),
            file_upload_entregables(),
            spacing="2",
            width="100%",
        )
except Exception as e:
    print(f"An error occurred: {e}")

@template(route="/agregarReglas", title="Agregar Reglas")
def agregarReglas() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir el excel de datos de las REGLAS", size="5"),
            rx.button(
                "REGRESAR",
                on_click=rx.redirect("/reglas"),  
                color_scheme="blue",
                variant="solid",
                size="2", 
            ),
            spacing="9",  
            align_items="center",
        ),
        file_upload_reglas(),
        spacing="2",
        width="100%",
    )

@template(route="/agregarProyectos", title="Agregar Proyectos")
def agregarProyectos() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir el excel de datos para los proyectos", size="5"),
            rx.button(
                "REGRESAR",
                on_click=rx.redirect("/proyectos"),  
                color_scheme="blue",
                variant="solid",
                size="2", 
            ),
            spacing="9",  
            align_items="center",
        ),
        file_upload_proyectos(),
        spacing="2",
        width="100%",
    )