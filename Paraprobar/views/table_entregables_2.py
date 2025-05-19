import reflex as rx

from ..models.entregables import vistaentregablesproyectos
from ..backend.entragables_state import EntragablesState
import os

# Obtener el nombre de usuario de la PC
USER_NAME = os.getlogin()

def _header_cell(text: str,options: list[str] = None, style: dict = None) -> rx.Component:
    options = [] if options is None else options
    style = style or {}

    children = []
    children.append(rx.text(text))

    # Función para manejar el cambio en el select
    def handle_filter_change(value: str):
        return EntragablesState.set_filter(text, value)

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
                        EntragablesState.filters.get(text) == "",
                        "",
                        EntragablesState.filters.get(text, "")
                    ),
                    width="38px",  # o el valor que desees
                ),
            ),
            align_items="center",
            spacing="0",
        ),
        style=style
    )

def _show_item_entregables(item: vistaentregablesproyectos, index: int,column_widths) -> rx.Component:
    def safe_path(path):
        return rx.cond(
            path,
            "http://localhost:8011/" +
            path.replace("https://cobraperusa.sharepoint.com/sites/Enginuity/Shared Documents/", "Base_de_datos_Ingenieria - Documentos/"),
            None
        )

    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))

    padding_style = {"padding": "13px 6px 12px 6px"}

    return rx.table.row(
        rx.table.cell(item.id,  style={**padding_style, "width": column_widths[0]}),
        rx.table.cell(item.codigo_proyecto_entregables, style={**padding_style, "width": column_widths[1]}),
        rx.table.cell(item.cliente, style={**padding_style, "fontSize": "0.7rem", "width": column_widths[2]}),
        rx.table.cell(item.nombre_proyecto, style={**padding_style, "fontSize": "0.7rem", "width": column_widths[3]}),
        rx.table.cell(item.disciplina_entregables, style={**padding_style, "width": column_widths[4]}),
        rx.table.cell(item.tipo_entregable_entre, style={**padding_style, "width": column_widths[5]}),
        rx.table.cell(item.codigo_entregable, style={**padding_style, "width": column_widths[6]}),
        rx.table.cell(item.nombre_entregable, style={**padding_style, "fontSize": "0.9rem", "width": column_widths[7]}),
        rx.table.cell(item.total_hh if item.total_hh is not None else "", style={**padding_style, "width": column_widths[8]}),
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
                rx.code(EntragablesState.page_number),
                f" of {EntragablesState.total_pages}",
                justify="end",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=EntragablesState.first_page,
                    opacity=rx.cond(EntragablesState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(EntragablesState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=EntragablesState.prev_page,
                    opacity=rx.cond(EntragablesState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(EntragablesState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=EntragablesState.next_page,
                    opacity=rx.cond(
                        EntragablesState.page_number == EntragablesState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        EntragablesState.page_number == EntragablesState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=EntragablesState.last_page,
                    opacity=rx.cond(
                        EntragablesState.page_number == EntragablesState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        EntragablesState.page_number == EntragablesState.total_pages,
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
                on_drop=EntragablesState.handle_upload_entregables,
                max_size=100_000_000,
                

            ),
            rx.cond(
                EntragablesState.upload_success,
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
    # Define un ancho fijo por columna para mantener la alineación
    column_widths = [
        "40px",   # ID
        "125.13px",  # Cod Pry
        "120px",  # Cliente
        "160px",  # Proyecto
        "120px",  # Disciplina
        "130px",  # Tipo Entrgbl
        "180px",  # Codigo Entrgbl
        "180px",  # Nombre Entrgbl
        "100px",  # HH Venta
        "80px",   # PDF
        "100px",  # Editable
    ]
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
                        on_click=lambda: [
                            EntragablesState.set_search_value_entregables(""),
                            EntragablesState.perform_search("")  # Limpiar la búsqueda también
                        ],
                        display=rx.cond(EntragablesState.search_value_entregables, "flex", "none"),
                    ),
                    value=EntragablesState.search_value_entregables,
                    placeholder="Buscar por entregables",
                    on_change=lambda value: [
                        EntragablesState.set_search_value_entregables(value),
                        EntragablesState.perform_search(value)
                    ],
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
            rx.vstack(
                # Scroll horizontal compartido
                rx.box(
                    rx.vstack(
                        # Header fijo
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    _header_cell("ID", style={"padding": "13px 6px 12px 6px","width": column_widths[0]}),
                                    _header_cell("Cod Pry", options=EntragablesState.unique_codigo_proyectos_cod_pry, style={"padding": "13px 6px 12px 6px","width": column_widths[1]}),
                                    _header_cell("Cliente", options=EntragablesState.unique_codigo_proyectos_cliente, style={"padding": "13px 6px 12px 6px","width": column_widths[2]}),
                                    _header_cell("Proyecto", options=EntragablesState.unique_codigo_proyectos_nom_proy, style={"padding": "13px 6px 12px 6px","width": column_widths[3]}),
                                    _header_cell("Disciplina", options=EntragablesState.unique_codigo_proyectos_disciplina, style={"padding": "13px 6px 12px 6px","width": column_widths[4]}),
                                    _header_cell("Tipo Entrgbl", options=EntragablesState.unique_codigo_proyectos_tip_entre, style={"padding": "13px 6px 12px 6px","width": column_widths[5]}),
                                    _header_cell("Codigo Entrgbl", style={"padding": "13px 6px 12px 6px","width": column_widths[6]}),
                                    _header_cell("Nombre Entrgbl", style={"padding": "13px 6px 12px 6px","width": column_widths[7]}),
                                    _header_cell("HH Venta", style={"padding": "13px 6px 12px 6px","width": column_widths[8]}),
                                    _header_cell("PDF", "file-text", style={"padding": "13px 6px 12px 6px","width": column_widths[9]}),
                                    _header_cell("Editable", style={"padding": "13px 6px 12px 6px","width": column_widths[10]}),
                                )
                            ),
                            variant="surface",
                            size="3",
                            width="100%",
                            style={
                                "minWidth": "1400px",
                                "tableLayout": "fixed",
                                "position": "sticky",
                                "top": "0",
                            },
                        ),
                        # Body scrollable y sincronizado en ancho
                        rx.box(
                            rx.table.root(
                                rx.table.body(
                                    rx.foreach(
                                        EntragablesState.get_current_page_entregables,
                                        lambda item, index: _show_item_entregables(item, index, column_widths),
                                    ),
                                    style={"fontSize": "0.9rem"},
                                ),
                                variant="surface",
                                size="3",
                                width="100%",
                                style={
                                    "minWidth": "1400px",
                                    "tableLayout": "fixed"
                                },
                            ),
                            style={
                                "overflowY": "auto",
                                "maxHeight": "500px",
                            },
                        ),
                    ),
                    style={"overflowX": "auto", "width": "100%"},
                ),
            ),
            id="scroll-bottom",
            style={"maxWidth": "100%", "overflowX": "auto"},
        ),


        _pagination_view(),
        # Sección de resultados de búsqueda dinámica
        rx.box(
            rx.cond(
                EntragablesState.search_value_entregables != "",
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
                            f"Búsqueda: '{EntragablesState.search_value_entregables}'", 
                            size="2", 
                            color="slate.500",
                            font_style="italic"
                        ),
                        padding_bottom="1em"
                    ),
                    rx.divider(border_color="slate.200"),
                    
                    rx.cond(
                        EntragablesState.elasticsearch_loading,
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
                                EntragablesState.elasticsearch_error,
                                rx.callout(
                                    EntragablesState.elasticsearch_error,
                                    icon="alert-triangle",
                                    color_scheme="red",
                                    width="100%",
                                    variant="soft",
                                    margin_bottom="1em"
                                ),
                                rx.fragment()
                            ),
                            
                            rx.cond(
                                EntragablesState.elasticsearch_results.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        EntragablesState.elasticsearch_results,
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
        ),
        width="100%",
    )