# pdf_viewer.py
import reflex as rx

class PDFState(rx.State):
    pdf_url: str = ""
    pdf_name: str = ""
    show_pdf: bool = False

    @classmethod
    def set_pdf_data(cls, name: str, url: str, show: bool):
        cls.pdf_name = name
        cls.pdf_url = url
        cls.show_pdf = show

    @classmethod
    def pdf_viewer_component(cls) -> rx.Component:
        return rx.cond(
            cls.show_pdf,
            rx.vstack(
                rx.hstack(
                    rx.icon("circle_check", size=20, color="green"),
                    rx.text(f"Archivo subido: {cls.pdf_name}"),
                ),
                rx.html(
                    f'<iframe src="{cls.pdf_url}" width="100%" height="500px" style="border: none;"></iframe>',
                    key=f"pdf-viewer-{cls.pdf_name}",
                ),
            ),
            rx.vstack(
                rx.text(f"DEBUG: PDF URL -> {cls.pdf_url}"),
                rx.text(f"DEBUG: PDF NAME -> {cls.pdf_name}"),
                rx.text(f"valor de show_pdf -> {cls.show_pdf}"),
            ),
        )