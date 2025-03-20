import reflex as rx
from ..backend.table_entregables_state import TableEntregablesState
from ..templates import template
from ..views.table_entregables import main_table
from ..views.table_entregables_2 import main_table_2
from ..backend.table_state import TableState

@template(route="/entregables", title="Entregables_River", on_load=TableEntregablesState.load_entries)
def entregables() -> rx.Component:
    return rx.vstack(
        rx.heading("Tabla de Entregables", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )

@template(route="/", title="Entregables", on_load=[TableState.start_loading, TableState.load_entries_entregables])
def entregables_2() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Entregables", size="7",align="center"),
        # Barra de carga
        rx.progress(
            value=TableState.loading_progress,
            width="100%",
            color="blue",
            size="3",
            display=rx.cond(TableState.loading_progress > 0, "block", "none"),
        ),        
        main_table_2(),
        spacing="8",
        width="100%",
    )
