
import reflex as rx

from ..backend.reglas_state import ReglasState
from ..templates import template
from ..views.table_reglas import main_table


@template(route="/reglas", title="Reglas",on_load=ReglasState.load_entries_reglas)
def reglas() -> rx.Component:

    return rx.vstack(
        rx.heading("Listado de Reglas", size="7",align="center"),
        main_table(),
        spacing="8",
        width="100%",
    )