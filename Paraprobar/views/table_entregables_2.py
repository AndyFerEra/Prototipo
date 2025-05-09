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
    # Función segura para generar URLs
    # En tu backend, antes de crear los objetos Entregables:
    def safe_path(path):
        # Usar rx.cond para manejar el tipo Var
        return rx.cond(
            path,
            "http://localhost:8011/" + 
            path.replace("C:\\Users\\Leo\\COBRA PERU S.A\\", "")
                .replace("C:/Users/Leo/COBRA PERU S.A/", "")
                .replace("\\", "/")
                .replace("//", "/")
                .replace("C:/Users/Leo/COBRA PERU S.A/", ""),
            None  # Si path es None o no válido
        )
        
    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))

    return rx.table.row(
        rx.table.cell(item.id),
        rx.table.cell(item.codigo_proyecto_entregables),
        rx.table.cell(item.cliente),
        rx.table.cell(item.nombre_proyecto),
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
        # Controles superiores (se mantiene igual)
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

        # Contenedor principal con scroll horizontal
        rx.box(
            # Tabla con ancho fijo
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            _header_cell("ID"),
                            _header_cell("Cod Pry", options=TableState.unique_codigo_proyectos_cod_pry),
                            _header_cell("Cliente", options=TableState.unique_codigo_proyectos_cliente),
                            _header_cell("Proyecto", options=TableState.unique_codigo_proyectos_nom_proy),
                            _header_cell("Disciplina", options=TableState.unique_codigo_proyectos_disciplina),
                            _header_cell("Tipo Entrgbl", options=TableState.unique_codigo_proyectos_tip_entre),
                            _header_cell("Codigo Entrgbl"),
                            _header_cell("Nombre Entrgbl"),
                            _header_cell("HH Venta"),
                            _header_cell("PDF", "file-text"),
                            _header_cell("Editable"),
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
                    width="max-content",  # Ancho según contenido
                    min_width="100%",     # Mínimo ancho del contenedor
                ),
            ),
            overflow_x="auto",
            max_height="70vh",          # Altura máxima
            border="1px solid #e2e8f0",
            borderRadius="lg",
            padding="1px",
            id="scroll-container",
        ),

        # Paginación
        _pagination_view(),
        
        # Sección de resultados de búsqueda dinámica
        rx.box(
            rx.cond(
                TableState.search_value_entregables != "",
                rx.vstack(
                    rx.heading(
                        "Resultados en contenido de entregables", 
                        size="6",
                        color="slate.800",
                        font_weight="semibold",
                        padding_bottom="0.5em"
                    ),
                    rx.box(
                        rx.text(
                            f"Búsqueda: '{TableState.search_value_entregables}'", 
                            size="2", 
                            color="slate.500",
                            font_style="italic"
                        ),
                        padding_bottom="1em"
                    ),
                    rx.divider(border_color="slate.200"),
                    
                    rx.cond(
                        TableState.elasticsearch_loading,
                        rx.center(
                            rx.spinner(
                                size="3",
                                color="blue.500",
                                thickness="3px",
                                speed="1s"
                            ), 
                            padding="6"
                        ),
                        
                        rx.box(
                            rx.cond(
                                TableState.elasticsearch_error,
                                rx.callout(
                                    TableState.elasticsearch_error,
                                    icon="alert-triangle",
                                    color_scheme="red",
                                    width="100%",
                                    variant="soft",
                                    margin_bottom="1em"
                                ),
                                rx.fragment()
                            ),
                            
                            rx.cond(
                                TableState.elasticsearch_results.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        TableState.elasticsearch_results,
                                        lambda item: rx.card(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.badge(
                                                        "Código de Entregable:",
                                                        color_scheme="blue",
                                                        variant="soft"
                                                    ),
                                                    rx.text(
                                                        item["codigo"],
                                                        weight="medium"
                                                    ),
                                                    rx.badge(
                                                        "Página:",
                                                        color_scheme="blue",
                                                        variant="soft"
                                                    ),
                                                    rx.text(
                                                        item["pagina"],
                                                        weight="medium"
                                                    ),
                                                    spacing="3",
                                                    align="center"
                                                ),
                                                rx.divider(border_color="slate.100"),
                                                rx.box(
                                                    rx.cond(
                                                        item["highlight"],
                                                        rx.html(
                                                            item["highlight"],
                                                            style={
                                                                "line-height": "1.5",
                                                                "font-size": "0.9em"
                                                            }
                                                        ),
                                                        rx.text(
                                                            item["texto"], 
                                                            color="slate.600",
                                                            size="2"
                                                        )
                                                    ),
                                                    padding="3",
                                                    bg="slate.50",
                                                    border_radius="lg",
                                                ),
                                                rx.link(
                                                    rx.button(
                                                        rx.text("Ver PDF en página "), 
                                                        rx.text(item["pagina"]),
                                                        size="2",
                                                        variant="solid",
                                                        color_scheme="blue",
                                                        right_icon="arrow-up-right"
                                                    ),
                                                    href=item["enlace"],
                                                    is_external=True
                                                ),
                                                spacing="3",
                                                padding="0.5em"
                                            ),
                                            width="100%",
                                            margin_bottom="1.5em",
                                            box_shadow="sm",
                                            _hover={
                                                "box_shadow": "md",
                                                "transform": "translateY(-2px)",
                                                "transition": "all 0.2s"
                                            }
                                        )
                                    ),
                                    spacing="3",  # El spacing debe estar en el vstack que contiene el foreach
                                    width="100%",
                                    padding_top="0.5em"
                                ),
                                
                                rx.callout(
                                    "No se encontraron resultados para esta búsqueda",
                                    icon="info",
                                    color_scheme="blue",
                                    variant="soft",
                                    width="100%"
                                )
                            )
                        )
                    ),
                    spacing="4",
                    width="100%"
                )
            ),
            margin_top="2.5em",
            padding_x="1em",
            width="100%"
        )
    )
