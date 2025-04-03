import reflex as rx

from Paraprobar.models.excel_data import Entregables
from ..backend.table_state import TableState
from ..components.status_badge import status_badge
import time

#personalizacion del encabezado de tabla
def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )

def _show_item_entregables(item: Entregables, index: int) -> rx.Component:
    # Función segura para generar URLs
    def safe_path(path):
        return rx.cond(
            path,
            f"http://localhost:8011/{path.replace('C:\\Users\\Leo\\COBRA PERU S.A\\', '').replace('\\', '/')}",
            "#"
        )

    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))

    return rx.table.row(
        rx.table.cell(item.id),
        rx.table.cell(item.codigo_proyecto_entregables),
        rx.table.cell(item.disciplina_entregables),
        rx.table.cell(item.tipo_entregable_entre),
        rx.table.cell(item.codigo_entregable),
        rx.table.cell(item.nombre_entregable),
        rx.table.cell(item.total_hh if item.total_hh is not None else ""),
        rx.table.cell(
            rx.cond(
                item.enlace_pdf,
                rx.link(
                    rx.hstack(
                        rx.text("PDF"),
                        rx.icon("file-text", size=20),
                        align="center",
                        spacing="1",
                    ),
                    href=safe_path(item.enlace_pdf),
                    target="_blank",
                    style={"color": "green"},
                ),
                rx.text("-")
            )
        ),
        rx.table.cell(
            rx.cond(
                item.enlace_nativo,
                rx.link(
                    rx.hstack(
                        rx.text("ORIGINAL"),
                        rx.icon("file", size=20),
                        align="center",
                        spacing="1",
                    ),
                    href=safe_path(item.enlace_nativo),
                    target="_blank",
                    style={"color": "blue"},
                ),
                rx.text("-")
            )
        ),
        style={"_hover": {"bg": hover_color}, "bg": bg_color},
        align="center",
    )

#sin decir pa la paginacion
def _pagination_view() -> rx.Component:
    return (
        rx.hstack(
            rx.text(
                "Page ",
                rx.code(TableState.page_number),
                f" of {TableState.total_pages}",
                justify="end",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=TableState.first_page,
                    opacity=rx.cond(TableState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(TableState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=TableState.prev_page,
                    opacity=rx.cond(TableState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(TableState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=TableState.next_page,
                    opacity=rx.cond(
                        TableState.page_number == TableState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        TableState.page_number == TableState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=TableState.last_page,
                    opacity=rx.cond(
                        TableState.page_number == TableState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        TableState.page_number == TableState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                align="center",
                spacing="2",
                justify="end",
            ),
            spacing="5",
            margin_top="1em",
            align="center",
            width="100%",
            justify="end",
        ),
    )

def file_upload_entregables() -> rx.Component:
    try:
        return rx.box(
            rx.heading("Subir Archivo los entregables", size="3", margin_bottom="1rem", color="#2D3748"),
            rx.upload(
                rx.box(
                    rx.vstack(
                        rx.icon("file-up", size=48, color="#2563EB"),  # Nuevo ícono
                        rx.text("Arrastra y suelta tu archivo aquí", font_size="1.2rem", font_weight="bold", color="#1F2937"),
                        rx.text("o haz clic para seleccionar un archivo", font_size="0.9rem", color="#4B5563"),
                    ),
                    max_size=100_000_000,
                    accept={
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                            "application/vnd.ms-excel": [".xls"]
                    },
                    padding="1rem",  # Reducir el padding
                    border="2px dashed #2563EB",
                    border_radius="12px",
                    height="200px",  # Reducir la altura
                    width="100%",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background_color="#E5E7EB",  # Fondo gris claro para mejorar contraste
                    _hover={"background_color": "#D1D5DB"},
                ),
                
                multiple=False,
                on_drop=TableState.handle_upload_entregables,
                max_size=100_000_000,
                

            ),
            rx.cond(
                TableState.upload_success,
                rx.text("Archivo subido y procesado correctamente.", color="green", margin_top="1rem"),
                rx.text("Esperando archivo....", color="#374151", margin_top="1rem"),  # Texto oscuro para contraste
                
            ),
            padding="1rem",  # Reducir el padding
            width="100%",
            max_width="400px",  # Reducir el ancho máximo
            border_radius="12px",
            box_shadow="lg",
            background_color="#F3F4F6",  # Fondo gris suave
            margin="auto",
        )
    except Exception as e:
        print(f"An error occurred: {e}")

def main_table_2() -> rx.Component:
    return rx.box(
        #ordenar mayor menor y busqueda y boton de descarga
        rx.flex(
            #ordenar mayor menor y busqueda 
            rx.flex(
                #condicional para cambiar el orden de los iconos de ordenar la tabla 
                rx.cond(
                    TableState.sort_reverse_entregables,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort_entregables,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort_entregables,
                    ),
                ),
                #combo box para ordenar la tabla
                rx.select(
                    [
                        "pipeline",
                        "status",
                        "workflow",
                        "timestamp",
                        "duration",
                    ],
                    placeholder="Sort By: Pipeline",
                    size="3",
                    cursor="pointer",
                    on_change=TableState.set_sort_value,
                ),
                #todo pa buscar
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("eraser"),
                        justify="end",
                        cursor="pointer",
                        on_click=lambda: TableState.set_search_value_entregables(""),  # Limpiar búsqueda
                        display=rx.cond(TableState.search_value_entregables, "flex", "none"),
                    ),
                    value=TableState.search_value_entregables,
                    placeholder="Buscar...",
                    on_change=TableState.set_search_value_entregables,  # Actualizar al escribir
                    width="100%",
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            # nuevo botón de descarga de plantilla
            rx.button(
                rx.icon("arrow-down-to-line", size=20),
                "Descargar Plantilla",
                size="3",
                variant="solid",
                cursor="pointer",
                on_click=rx.download(url="/prueba.xlsx"),
            ),
            #boton de descarga
            rx.button(
                rx.icon("square-plus", size=20),
                "Agregar",
                size="3",
                color_scheme="green",
                cursor="pointer",
                variant="solid",
                display=["none", "none", "none", "flex"],
                on_click=rx.redirect("/agregarEntregables"),
            ),
            spacing="3",
            justify="between",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                #iconos y nombre del encabezado de tabla
                rx.table.row(
                    _header_cell("ID", "hash"),
                    _header_cell("Codigo Pry", "folder-git"),
                    _header_cell("Disciplina", "list-collapse"),
                    _header_cell("Tipo Entrgbl", "square-stack"),
                    _header_cell("Codigo Entrgbl", "folder-code"),
                    _header_cell("Nombre Entrgbl", "folder-pen"),
                    _header_cell("HH Venta", "hourglass"),
                    _header_cell("PDF", "file-text"),
                    _header_cell("Editable", "pencil-line"),
                ),
            ),
            rx.table.body( 
                rx.foreach(
                    TableState.get_current_page_entregables,
                    lambda item, index: _show_item_entregables(item, index),
                ),
                style={"fontSize": "0.9rem"}
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        _pagination_view(),
        width="100%",
    )
