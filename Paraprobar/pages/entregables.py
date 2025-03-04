import reflex as rx

from ..backend.table_state import TableState
from ..templates import template
from ..views.table_entregables import main_table


@template(route="/", title="Entregables", on_load=TableState.load_entries)
def entregables() -> rx.Component:
   
    return rx.vstack(
        rx.heading("Listado de Entregables", size="7",align="center"),
        main_table(),
        spacing="8",
        width="100%",
    )
