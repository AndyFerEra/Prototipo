
import reflex as rx

from ..backend.proyectos_state import ProyectosState
from ..templates import template
from ..views.table_proyectos import main_table


@template(route="/proyectos", title="Proyectos",on_load=ProyectosState.load_entries_proyectos)
def proyectos() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Proyectos", size="7",align="center"),
        main_table(),
        spacing="8",
        width="100%",
    )

