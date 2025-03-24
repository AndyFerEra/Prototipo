import reflex as rx
from typing import Dict, Any, List
#Actualizar las importaciones en cualquier archivo que use excel_viewer.py para que use excel_editor.py en su lugar.
def excel_viewer(
    sheet_data: Dict[str, Any],
    sheet_names: List[str],
    current_sheet: str,
    on_sheet_change: Any,
) -> rx.Component:
    """Componente para visualizar datos de Excel."""
    if not sheet_data:
        return rx.box(
            rx.text("No hay datos para mostrar"),
            padding="2em",
            text_align="center"
        )
    
    return rx.vstack(
        # Selector de hojas
        rx.hstack(
            rx.text("Hoja:"),
            rx.select(
                sheet_names,
                value=current_sheet,
                on_change=on_sheet_change,
                width="200px",
            ),
            width="100%",
            padding="1em",
            background="white",
            border_bottom="1px solid #eee",
        ),
        
        # Tabla de datos
        rx.box(
            rx.table(
                rx.thead(
                    rx.tr(
                        rx.foreach(
                            sheet_data.get('columns', []),
                            lambda col: rx.th(
                                col,
                                padding="0.5em",
                                border="1px solid #eee",
                                background="#f5f5f5",
                                font_weight="bold",
                            )
                        )
                    )
                ),
                rx.tbody(
                    rx.foreach(
                        sheet_data.get('data', []),
                        lambda row: rx.tr(
                            rx.foreach(
                                sheet_data.get('columns', []),
                                lambda col: rx.td(
                                    str(row.get(col, "")),
                                    padding="0.5em",
                                    border="1px solid #eee",
                                )
                            )
                        )
                    )
                ),
                width="100%",
                border_collapse="collapse",
            ),
            overflow="auto",
            max_height="500px",
        ),
        width="100%",
        background="white",
        border_radius="md",
        border="1px solid #eee",
    )