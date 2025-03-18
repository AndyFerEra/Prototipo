import reflex as rx

from ..backend.table_state import TableState
from ..templates import template
from ..views.table import main_table

from reflex.components.core.breakpoints import Breakpoints


@template(route="/", title="Dashboard", on_load=TableState.load_entries)
def dashboard() -> rx.Component:
    """The dashboard page."""
    return rx.vstack(
        rx.heading("Gestor de Documentos", size="5"),

        rx.flex(
            rx.card(
                rx.vstack(
                    rx.icon("file_archive", size=40, color="green"),
                    rx.heading("Excel", size="4"),
                    rx.text("Subir y visualizar archivos Excel"),
                    rx.flex(
                        rx.button(
                            "Subir Excel",
                            on_click=rx.redirect("/agregar"),
                            color_scheme="green",
                            variant="solid",
                        ),
                        rx.button(
                            "Ver Excel",
                            on_click=rx.redirect("/visualizar-excel"),
                            color_scheme="gray",
                            variant="soft",
                        ),
                        width="100%",
                        justify="between",
                    ),
                    spacing="4",
                    align_items="center",
                    padding="1em",
                ),
                width="100%",
            ),

            rx.card(
                rx.vstack(
                    rx.icon("file_archive", size=40, color="blue"),
                    rx.heading("PDF", size="4"),
                    rx.text("Subir y visualizar archivos PDF"),
                    rx.flex(
                        rx.button(
                            "Subir PDF",
                            on_click=rx.redirect("/subir-pdf"),
                            color_scheme="blue",
                            variant="solid",
                        ),
                        rx.button(
                            "Ver Metadatos",
                            on_click=rx.redirect("/visualizar-metadatos"),
                            color_scheme="gray",
                            variant="soft",
                        ),
                        width="100%",
                        justify="between",
                    ),
                    spacing="4",
                    align_items="center",
                    padding="1em",
                ),
                width="100%",
            ),
            
            spacing="4",
            width="100%",
            direction=Breakpoints(base='column', md='column', lg='row'),
        ),
        
        rx.heading("Datos almacenados", size="4", margin_top="1em"),
        main_table(),
        
        spacing="8",
        width="100%",
        padding="1em",
    )