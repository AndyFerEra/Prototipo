import reflex as rx
from ..backend.table_entregables_state import TableEntregablesState
from ..models.entregable_model import Entregable

def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )

def _show_item(item: Entregable, index: int) -> rx.Component:
    bg_color = rx.cond(index % 2 == 0, rx.color("gray", 1), rx.color("accent", 2))
    hover_color = rx.cond(index % 2 == 0, rx.color("gray", 3), rx.color("accent", 3))
    return rx.table.row(
        rx.table.cell(item.id),
        rx.table.cell(item.nombre_entregable),
        rx.table.cell(item.codigo_proyecto),
        rx.table.cell(item.disciplina),
        rx.table.cell(item.clasificacion_entregable),
        rx.table.cell(item.tipo_entregable),
        rx.table.cell(item.codigo_entregable),
        rx.table.cell(item.total_hh),
        style={"_hover": {"bg": hover_color}, "bg": bg_color},
        align="center",
    )

def _pagination_view() -> rx.Component:
    return rx.hstack(
        rx.text(
            "Page ", rx.code(TableEntregablesState.page_number), f" of {TableEntregablesState.total_pages}",
            justify="end",
        ),
        rx.hstack(
            rx.icon_button(
                rx.icon("chevrons-left", size=18),
                on_click=TableEntregablesState.first_page,
                opacity=rx.cond(TableEntregablesState.page_number == 1, 0.6, 1),
                color_scheme=rx.cond(TableEntregablesState.page_number == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-left", size=18),
                on_click=TableEntregablesState.prev_page,
                opacity=rx.cond(TableEntregablesState.page_number == 1, 0.6, 1),
                color_scheme=rx.cond(TableEntregablesState.page_number == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-right", size=18),
                on_click=TableEntregablesState.next_page,
                opacity=rx.cond(TableEntregablesState.page_number == TableEntregablesState.total_pages, 0.6, 1),
                color_scheme=rx.cond(TableEntregablesState.page_number == TableEntregablesState.total_pages, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevrons-right", size=18),
                on_click=TableEntregablesState.last_page,
                opacity=rx.cond(TableEntregablesState.page_number == TableEntregablesState.total_pages, 0.6, 1),
                color_scheme=rx.cond(TableEntregablesState.page_number == TableEntregablesState.total_pages, "gray", "accent"),
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
    )

def main_table() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.cond(
                    TableEntregablesState.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a", size=28, stroke_width=1.5, cursor="pointer", flex_shrink="0",
                        on_click=TableEntregablesState.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z", size=28, stroke_width=1.5, cursor="pointer", flex_shrink="0",
                        on_click=TableEntregablesState.toggle_sort,
                    ),
                ),
                rx.select(
                    [
                        "id",
                        "nombre_entregable",
                        "codigo_proyecto",
                        "disciplina",
                        "clasificacion_entregable",
                        "tipo_entregable",
                        "codigo_entregable",
                        "total_hh",
                    ],
                    placeholder="Ordenar por: Nombre Entregable",
                    size="3",
                    on_change=TableEntregablesState.set_sort_value,
                ),
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("x"),
                        justify="end",
                        cursor="pointer",
                        on_click=TableEntregablesState.set_search_value(""),
                        display=rx.cond(TableEntregablesState.search_value, "flex", "none"),
                    ),
                    value=TableEntregablesState.search_value,
                    placeholder="Buscar...",
                    size="3",
                    max_width=["150px", "150px", "200px", "250px"],
                    width="100%",
                    variant="surface",
                    color_scheme="gray",
                    on_change=TableEntregablesState.set_search_value,
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            spacing="3",
            justify="between",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("ID", "hash"),
                    _header_cell("Nombre Entregable", "file-text"),
                    _header_cell("Código Proyecto", "folder"),
                    _header_cell("Disciplina", "layers"),
                    _header_cell("Clasificación", "tag"),
                    _header_cell("Tipo Entregable", "type"),
                    _header_cell("Código Entregable", "code"),
                    _header_cell("Total HH", "clock"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    TableEntregablesState.get_current_page,
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