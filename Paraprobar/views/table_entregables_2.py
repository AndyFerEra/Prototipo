import reflex as rx

from ..models.excel_data import Entregables,vistaentregablesproyectos
from ..backend.table_state import TableState
import os

# Obtener el nombre de usuario de la PC
USER_NAME = os.getlogin()

def _header_cell(text: str, icon: str = None, options: list[str] = None, style: dict = None) -> rx.Component:
    options = [] if options is None else options
    style = style or {}

    children = [rx.icon(icon, size=18)] if icon else []
    children.append(rx.text(text))

    # Función para manejar el cambio en el select
    def handle_filter_change(value: str):
        return TableState.set_filter(text, value)

    return rx.table.column_header_cell(
        rx.hstack(
            *children,
            rx.cond(
                options,
                rx.select(
                    # Añadimos placeholder y manejamos el valor actual
                    options,
                    
                    on_change=handle_filter_change,
                    value=rx.cond(
                        TableState.filters.get(text) == "",
                        "",
                        TableState.filters.get(text, "")
                    ),
                    width="0px 0px 10px 0px",
                ),
                rx.box()
            ),
            align_items="center",
            spacing="0",
        ),
        style=style
    )

def _show_item_entregables(item: vistaentregablesproyectos, index: int) -> rx.Component:
    def safe_path(path):
        return rx.cond(
            path,
            "http://localhost:8011/" +
            path.replace("https://cobraperusa.sharepoint.com/sites/Enginuity/Shared Documents/", "Base_de_datos_Ingenieria - Documentos/"),
            None
        )

    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))

    padding_style = {"padding": "13px 6px 12px 9px"}

    return rx.table.row(
        rx.table.cell(item.id, style=padding_style),
        rx.table.cell(item.codigo_proyecto_entregables, style=padding_style),
        rx.table.cell(item.cliente, style={**padding_style, "fontSize": "0.7rem"}),
        rx.table.cell(item.nombre_proyecto, style={**padding_style, "fontSize": "0.7rem"}),
        rx.table.cell(item.disciplina_entregables, style=padding_style),
        rx.table.cell(item.tipo_entregable_entre, style=padding_style),
        rx.table.cell(item.codigo_entregable, style=padding_style),
        rx.table.cell(item.nombre_entregable, style={**padding_style, "fontSize": "0.9rem"}),
        rx.table.cell(item.total_hh if item.total_hh is not None else "", style=padding_style),
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
            ),
            style=padding_style,
        ),
        rx.table.cell(
            rx.cond(
                item.enlace_nativo,
                rx.link(
                    rx.hstack(
                        rx.text("ORIGINAL", style={"fontSize": "0.8rem"}),
                        rx.icon("file", size=20),
                        align="center",
                        spacing="1",
                    ),
                    href=safe_path(item.enlace_nativo),
                    target="_blank",
                    style={"color": "blue"},
                ),
                rx.text("-", style={"fontSize": "0.8rem"})
            ),
            style=padding_style,
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
        # Controles superiores: búsqueda y botones
        rx.flex(
            rx.flex(
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("eraser"),
                        justify="end",
                        cursor="pointer",
                        on_click=lambda: TableState.set_search_value_entregables(""),
                        display=rx.cond(TableState.search_value_entregables, "flex", "none"),
                    ),
                    value=TableState.search_value_entregables,
                    placeholder="Buscar por entregables",
                    on_change=TableState.set_search_value_entregables,
                    width="100%",
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            rx.button(
                rx.icon("arrow-down-to-line", size=20),
                "Descargar Plantilla",
                size="3",
                variant="solid",
                cursor="pointer",
                on_click=rx.download(url="/prueba.xlsx"),
            ),
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
        # Tabla con scroll horizontal real
        rx.box(
            rx.table.root(
                
                rx.table.header(
                    rx.table.row(
                        
                        _header_cell("ID", style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Cod Pry", options=TableState.unique_codigo_proyectos_cod_pry, style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Cliente", options=TableState.unique_codigo_proyectos_cliente, style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Proyecto", options=TableState.unique_codigo_proyectos_nom_proy, style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Disciplina", options=TableState.unique_codigo_proyectos_disciplina, style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Tipo Entrgbl", options=TableState.unique_codigo_proyectos_tip_entre, style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Codigo Entrgbl", style={"padding": "13px 6px 12px 9px", "paddingRight": "210px"}),  # Se mantiene la personalización
                        _header_cell("Nombre Entrgbl", style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("HH Venta", style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("PDF", "file-text", style={"padding": "13px 6px 12px 9px"}),
                        _header_cell("Editable", style={"padding": "13px 6px 12px 9px"}),
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
            overflow_x="auto",
            max_width="100%",
            id="scroll-bottom",
        ),
        width="100%",
    )