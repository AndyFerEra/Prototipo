
import reflex as rx

from ..backend.table_state import TableState
from ..templates import template
from ..views.table_proyectos import main_table


@template(route="/proyectos", title="Proyectos",on_load=TableState.load_entries_proyectos)
def proyectos() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Proyectos", size="7",align="center"),
        main_table(),
        spacing="8",
        width="100%",
    )

