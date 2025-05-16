import reflex as rx
from ..templates import template
from ..views.table_entregables_2 import main_table_2
from ..backend.entragables_state import EntragablesState


@template(route="/", title="Entregables", on_load=[EntragablesState.load_entries_entregables])
def entregables_2() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Entregables", size="7", align="center"),
        # Barra de carga  
        main_table_2(),
        spacing="8",
        width="100%",
        padding="2",
    )
