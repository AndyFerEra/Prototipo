import reflex as rx
from ..backend.table_entregables_state import TableEntregablesState
from ..templates import template
from ..views.table_entregables import main_table

@template(route="/entregables", title="Entregables", on_load=TableEntregablesState.load_entries)
def entregables() -> rx.Component:
    return rx.vstack(
        rx.heading("Tabla de Entregables", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )