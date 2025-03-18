import reflex as rx
from ..backend.table_state import TableState
from ..templates import template
from ..views.excel_viewer import excel_viewer

@template(route="/agregar", title="Agregar Datos")
def agregar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Subir un nuevo Excel de datos", size="5"),
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
        
        rx.card(
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.icon("file_archive", size=40, color="green"),
                        rx.text("Arrastra y suelta tu archivo Excel aquí o haz clic para seleccionar"),
                    ),
                    border="1px dashed #ccc",
                    padding="2rem",
                    border_radius="md",
                    id="excel_upload",
                    accept={"application/vnd.ms-excel": [".xls", ".xlsx"]},
                    max_files=1,
                ),
                rx.button(
                    "Procesar Excel",
                    on_click=TableState.handle_upload(rx.upload_files(upload_id="excel_upload")),
                    color_scheme="green",
                    variant="solid",
                    margin_top="1em",
                ),
                rx.cond(
                    TableState.upload_success,
                    rx.text(f"Archivo {TableState.uploaded_file_name} cargado correctamente", color="green"),
                    rx.text(""),
                ),
                spacing="2",
                width="100%",
                align_items="center",
                padding="1em",
            ),
            width="100%",
        ),
        
        # Vista previa del cargado
        rx.cond(
            TableState.excel_data,
            rx.vstack(
                rx.heading("Vista previa del Excel", size="4"),
                excel_viewer(TableState.excel_data, TableState.excel_columns),
                spacing="4",
                width="100%",
            ),
            rx.text(""),
        ),
        
        # Botón para ver todos
        rx.cond(
            TableState.upload_success,
            rx.button(
                "Ver todos los archivos Excel",
                on_click=rx.redirect("/visualizar-excel"),
                color_scheme="green",
                variant="solid",
                margin_top="1em",
            ),
            rx.text(""),
        ),
        
        spacing="4",
        width="100%",
        padding="1em",
    )