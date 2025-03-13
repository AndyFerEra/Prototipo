import reflex as rx

def excel_viewer(excel_data: list[dict], columns: list[str]) -> rx.Component:
    if not excel_data or not columns:
        return rx.box(
            rx.text("No hay datos de Excel para mostrar"),
            padding="2em",
            text_align="center"
        )
    
    return rx.box(
        rx.data_table(
            data=excel_data,
            pagination=True,
            search=True,
            sort=True,
            resizable=True,
            selection="single",
        ),
        width="100%",
        padding="1em",
        border="1px solid #e2e8f0",
        border_radius="md",
        overflow="auto",
    )

def excel_file_list(excel_files: list[dict], on_select=None) -> rx.Component:
    if not excel_files:
        return rx.box(
            rx.text("No hay archivos Excel disponibles"),
            padding="1em",
            text_align="center"
        )
    
    return rx.box(
        rx.heading("Archivos Excel disponibles", size="4"),
        rx.list(
            rx.foreach(
                excel_files,
                lambda file: rx.list_item(
                    rx.button(
                        file["name"],
                        on_click=lambda: on_select(file["path"]) if on_select else None,
                        variant="soft",
                        width="100%",
                        justify="start",
                        padding="0.5em",
                    )
                )
            ),
            spacing="2",
            width="100%",
        ),
        padding="1em",
        border="1px solid #e2e8f0",
        border_radius="md",
        margin_bottom="1em",
    )
