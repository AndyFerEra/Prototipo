import reflex as rx
from ..backend.pdf_state import TableStatePDF

def file_upload_PDF() -> rx.Component:
    return rx.box(
        rx.heading("Subir PDF", size="3", margin_bottom="1rem", color="#e9004c"),
        rx.vstack(
            rx.upload(
                rx.button("Seleccionar archivo", background_color="#374151",color="white",),
                border="1px dashed #ccc",
                padding="1rem",
                border_radius="4px",
            ),
            rx.button(
                "Subir archivo",
                on_click=TableStatePDF.handle_upload(rx.upload_files()),
                margin_top="1rem",
                background_color="#e9004c",
                color="white",
            ),
            rx.cond(
                TableStatePDF.uploaded_file,
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle_check", size=20, color="#374151", margin_top="0.1rem",),
                        rx.text(f"Archivo subido: {TableStatePDF.uploaded_file}", font_weight="bold", color="#1e252b"),
                    ),
                    rx.html(
                        f"""
                        <div>
                            <iframe src="http://localhost:8001/static/uploads/{TableStatePDF.uploaded_file}" width="250%" height="500px" style="border: none;"></iframe>
                        </div>
                        """
                    ),
                    spacing="2",
                ),
            ),
            spacing="2",
        ),
        rx.cond(
            TableStatePDF.extracted_data,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Nombre del Entregable:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            on_change=TableStatePDF.set_nombre_entregable,
                            placeholder="Nombre del Entregable",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.nombre_entregable == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Nombre del Entregable",  # El texto flotante
                            placement="top",  # Ubicación del tooltip
                            background_color="#e9004c",  # Estilo
                            color="white",  # Color del texto
                            border_radius="6px",  # Bordes redondeados
                            padding="0.5rem",  # Espaciado interno
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.hstack(
                        rx.text("Código de proyecto:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            value=TableStatePDF.codigo_proyecto,
                            on_change=TableStatePDF.set_codigo_proyecto,
                            placeholder="Código de proyecto",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.codigo_proyecto == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Código de proyecto",
                            placement="top",
                            background_color="#e9004c",
                            color="white",
                            border_radius="6px",
                            padding="0.5rem",
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.hstack(
                        rx.text("Disciplina:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            value=TableStatePDF.disciplina,
                            on_change=TableStatePDF.set_disciplina,
                            placeholder="Disciplina",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.disciplina == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Disciplina",
                            placement="top",
                            background_color="#e9004c",
                            color="white",
                            border_radius="6px",
                            padding="0.5rem",
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.hstack(
                        rx.text("Clasificación de entregable:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            value=TableStatePDF.clasificacion_entregable,
                            on_change=TableStatePDF.set_clasificacion_entregable,
                            placeholder="Clasificación de entregable",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.clasificacion_entregable == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Clasificación de entregable",
                            placement="top",
                            background_color="#e9004c",
                            color="white",
                            border_radius="6px",
                            padding="0.5rem",
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.hstack(
                        rx.text("Tipo de entregable:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            value=TableStatePDF.tipo_entregable,
                            on_change=TableStatePDF.set_tipo_entregable,
                            placeholder="Tipo de entregable",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.tipo_entregable == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Tipo de entregable",
                            placement="top",
                            background_color="#e9004c",
                            color="white",
                            border_radius="6px",
                            padding="0.5rem",
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.hstack(
                        rx.text("Código de entregable:", width="150px", align="left", font_weight="bold", color="#1e252b"),
                        rx.input(
                            value=TableStatePDF.codigo_entregable,
                            on_change=TableStatePDF.set_codigo_entregable,
                            placeholder="Código de entregable",
                            aling="right",
                            width="70%",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle_alert",
                                size=20,
                                color="#e9004c",
                                display=rx.cond(
                                    TableStatePDF.codigo_entregable == "",
                                    "flex",
                                    "none"
                                ),
                            ),
                            content="Debe rellenar el campo Código de entregable",
                            placement="top",
                            background_color="#e9004c",
                            color="white",
                            border_radius="6px",
                            padding="0.5rem",
                        ),
                        width="100%",
                        justify_content="space-between",
                    ),
                    rx.center(
                        rx.button(
                            "Corregir y Guardar",
                            rx.icon("save", size=20, color="white"),
                            on_click=TableStatePDF.corregir_valores,
                            margin_top="2rem",
                            background_color="#e9004c",
                            color="white",
                            # Habilitar solo si todos los campos están completos
                            disabled=rx.cond(
                                (TableStatePDF.nombre_entregable == "") |
                                (TableStatePDF.codigo_proyecto == "") |
                                (TableStatePDF.disciplina == "") |
                                (TableStatePDF.clasificacion_entregable == "") |
                                (TableStatePDF.tipo_entregable == "") |
                                (TableStatePDF.codigo_entregable == ""),
                                True,
                                False
                            ),
                        ),
                    ),
                ),
                padding="1rem",
                width="100%",
                max_width="500px",
                border_radius="12px",
                box_shadow="lg",
                background_color="#F3F4F6",
                margin="auto",
            ),
        ),
        padding="1rem",
        width="200%",
        max_width="800px",
        border_radius="12px",
        box_shadow="lg",
        background_color="#F3F4F6",
        margin="auto",
    )