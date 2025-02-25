import reflex as rx

from Paraprobar.models.excel_data import ExcelData
from ..backend.table_state import Item, TableState
from ..components.status_badge import status_badge

#trae la informacion de la tabla para poder mostrarlo en diferentes vista
def _create_dialog(
    item: Item, icon_name: str, color_scheme: str, dialog_title: str
) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon(icon_name), color_scheme=color_scheme, size="2", variant="solid"
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(dialog_title),
                rx.dialog.description(
                    rx.vstack(
                        rx.text(item.pipeline),
                        rx.text(item.workflow),
                        status_badge(item.status),
                        rx.text(item.timestamp),
                        rx.text(item.duration),
                    )
                ),
                rx.dialog.close(
                    rx.button("Close Dialog", size="2", color_scheme=color_scheme),
                ),
            ),
        ),
    )

#para los botones falta la logica
def _delete_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "trash-2", "tomato", "Delete Dialog")


def _approve_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "check", "grass", "Approve Dialog")


def _edit_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "square-pen", "blue", "Edit Dialog")

#botones agrupados
def _dialog_group(item: Item) -> rx.Component:
    return rx.hstack(
        _approve_dialog(item),
        _edit_dialog(item),
        _delete_dialog(item),
        align="center",
        spacing="2",
        width="100%",
    )

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

def _show_item(item: ExcelData, index: int) -> rx.Component:
    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))

    return rx.table.row(
        rx.table.cell(item.id),
        rx.table.cell(item.nombre),
        rx.table.cell(item.edad),  # Convertimos edad a string
        rx.table.cell(item.email),
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

def file_upload() -> rx.Component:
    return rx.box(
        rx.heading("Subir Archivo", size="3", margin_bottom="1rem", color="#2D3748"),
        rx.upload(
            rx.box(
                rx.vstack(
                    rx.icon("file-up", size=48, color="#2563EB"),  # Nuevo ícono
                    rx.text("Arrastra y suelta tu archivo aquí", font_size="1.2rem", font_weight="bold", color="#1F2937"),
                    rx.text("o haz clic para seleccionar un archivo", font_size="0.9rem", color="#4B5563"),
                ),
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
            on_drop=TableState.handle_upload,
        ),
        rx.cond(
            TableState.upload_success,
            rx.text("Archivo subido y procesado correctamente.", color="green", margin_top="1rem"),
            rx.text("Esperando archivo...", color="#374151", margin_top="1rem"),  # Texto oscuro para contraste
        ),
        padding="1rem",  # Reducir el padding
        width="100%",
        max_width="400px",  # Reducir el ancho máximo
        border_radius="12px",
        box_shadow="lg",
        background_color="#F3F4F6",  # Fondo gris suave
        margin="auto",
    )
    

def main_table() -> rx.Component:
    return rx.box(
        #ordenar mayor menor y busqueda y boton de descarga
        rx.flex(
            #ordenar mayor menor y busqueda 
            rx.flex(
                #condicional para cambiar el orden de los iconos de ordenar la tabla 
                rx.cond(
                    TableState.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort,
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
                    on_change=TableState.set_sort_value,
                ),
                #todo pa buscar
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("x"),
                        justify="end",
                        cursor="pointer",
                        on_click=TableState.setvar("search_value", ""),
                        display=rx.cond(TableState.search_value, "flex", "none"),
                    ),
                    value=TableState.search_value,
                    placeholder="Search here...",
                    size="3",
                    max_width=["150px", "150px", "200px", "250px"],
                    width="100%",
                    variant="surface",
                    color_scheme="gray",
                    on_change=TableState.set_search_value,
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
                on_click=rx.download(url="/prueba.xlsx"),
            ),
            #boton de descarga
            rx.button(
                rx.icon("square-plus", size=20),
                "Agregar",
                size="3",
                color_scheme="green",
                variant="solid",
                display=["none", "none", "none", "flex"],
                on_click=rx.redirect("/agregar"),
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
                    _header_cell("Pipeline", "route"),
                    _header_cell("Workflow", "list-checks"),
                    _header_cell("Status", "notebook-pen"),
                    _header_cell("Timestamp", "calendar"),
                    _header_cell("Duration", "clock"),
                    _header_cell("Action", "cog"),
                ),
            ),
            rx.table.body( 
                rx.foreach(
                    TableState.get_current_page,
                    lambda item, index: _show_item(item, index),
                )
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        _pagination_view(),
        width="100%",
    )
