import reflex as rx
from ..templates import template
from ..views.table_entregables_2 import main_table_2
from ..backend.table_state import TableState



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
