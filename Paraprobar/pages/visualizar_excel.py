import reflex as rx
from ..backend.table_state import TableState
from ..templates import template
from ..views.excel_viewer import excel_viewer, excel_file_list

@template(route="/visualizar-excel", title="Visualizar Excel", on_load=TableState.on_load)
def visualizar_excel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Visualizar Excel", size="5"),
            rx.button(
                "REGRESAR",
                on_click=rx.redirect("/"),
                color_scheme="blue",
                variant="solid",
                size="2",
            ),
            spacing="9",
            align_items="center",
            width="100%",
        ),
        
        rx.flex(
            # Lista disponibles
            rx.box(
                excel_file_list(TableState.excel_files, on_select=TableState.view_excel),
                width="30%",
                padding="1em",
            ),
            
            # Visor
            rx.box(
                rx.cond(
                    TableState.excel_data,
                    excel_viewer(TableState.excel_data, TableState.excel_columns),
                    rx.text("Seleccione un archivo Excel para visualizar", padding="2em", text_align="center"),
                ),
                width="70%",
                padding="1em",
            ),
            width="100%",
            direction=["column", "column", "row"],
            spacing="4",
        ),
        
        spacing="4", 
        width="100%",
        padding="1em",
    )