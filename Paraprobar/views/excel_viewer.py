import reflex as rx

def excel_viewer(excel_data: list[dict], columns: list[str]) -> rx.Component:
    return rx.cond(
        excel_data & columns,
        rx.box(
            rx.data_table(
                data=excel_data,
                columns=columns,
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
        ),
        rx.box(
            rx.text("No hay datos de Excel para mostrar"),
            padding="2em",
            text_align="center"
        )
    )

def excel_file_list(excel_files: list[dict], on_select=None) -> rx.Component:
    return rx.cond(
        excel_files,
        rx.box(
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
        ),
        rx.box(
            rx.text("No hay archivos Excel disponibles"),
            padding="1em",
            text_align="center"
        )
    )
