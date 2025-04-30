import reflex as rx
from ..backend.excel_state import ExcelState
from ..components.excel_editor import handsontable_editor

def visualizar_excel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Editor de Excel", size="5"),
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
        
        # Barra de herramientas
        rx.hstack(
            rx.button(
                "Nueva Hoja",
                on_click=ExcelState.create_new_sheet,
                color_scheme="green",
                variant="solid",
            ),
            rx.upload(
                rx.button(
                    "Abrir Excel",
                    color_scheme="blue",
                    variant="solid",
                ),
                id="excel_upload",
                accept={
                    "application/vnd.ms-excel": [".xls"],
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"]
                },
                max_files=1,
                on_upload=ExcelState.handle_upload,
            ),
            rx.text(ExcelState.upload_status),
            width="100%",
            padding="1em",
            background="white",
            border_bottom="1px solid #eee",
        ),
        
        # Editor de Excel
        rx.cond(
            ExcelState.excel_data,
            handsontable_editor(
                ExcelState.excel_data,
                ExcelState.columns,
                height="600px",
            ),
            rx.vstack(
                rx.icon("table", size=40, color="gray.400"),
                rx.text(
                    "Crea una nueva hoja o abre un archivo Excel existente",
                    color="gray.500",
                ),
                padding="4em",
                spacing="4",
            ),
        ),
        
        spacing="4",
        width="100%",
        background="white",
        border_radius="md",
        border="1px solid #eee",
    )