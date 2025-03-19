import reflex as rx
from ..backend.table_entregables_state import TableEntregablesState
from ..templates import template
from ..views.table_entregables import main_table
from ..views.table_entregables_2 import main_table_2
from ..backend.table_state import TableState

@template(route="/entregables", title="Entregables", on_load=TableEntregablesState.load_entries)
def entregables() -> rx.Component:
    return rx.vstack(
        rx.heading("Tabla de Entregables", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )

@template(route="/", title="Entregables", on_load=TableState.load_entries_entregables)
def entregables_2() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Entregables", size="7",align="center"),
        main_table_2(),
        spacing="8",
        width="100%",
    )
