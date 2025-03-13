import reflex as rx

def pdf_viewer(pdf_path: str) -> rx.Component:
    if not pdf_path:
        return rx.box(
            rx.text("Seleccione un PDF para visualizar"),
            padding="2em",
            text_align="center"
        )
    
    return rx.box(
        rx.iframe(
            src=f"/pdfjs/web/viewer.html?file={pdf_path}",
            width="100%",
            height="600px",
            border="none",
        ),
        width="100%",
        border="1px solid #e2e8f0",
        border_radius="md",
        overflow="hidden",
    )

def pdf_file_list(pdf_files: list[dict], on_select=None) -> rx.Component:
    if not pdf_files:
        return rx.box(
            rx.text("No hay archivos PDF disponibles"),
            padding="1em",
            text_align="center"
        )
    
    return rx.box(
        rx.heading("PDFs disponibles", size="4"),
        rx.list(
            rx.foreach(
                pdf_files,
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