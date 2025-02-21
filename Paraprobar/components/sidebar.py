"""Componente Sidebar para la aplicación."""

import reflex as rx

from .. import styles

def sidebar_item_icon(icon: str) -> rx.Component:
    return rx.icon(icon, size=18)


def sidebar_item(text: str, url: str) -> rx.Component:
    """Elemento del Sidebar.

    Args:
        text: El texto del elemento.
        url: La URL del elemento.

    Returns:
        rx.Component: El componente del elemento del Sidebar.

    """
    # Si el elemento está activo.
    active = (rx.State.router.page.path == url.lower()) | (
        (rx.State.router.page.path == "/") & text == "Overview"
    )

    return rx.link(
        rx.hstack(
            rx.match(
                text,
                ("Dashboard", sidebar_item_icon("layout-dashboard")),
                ("About", sidebar_item_icon("book-open")),
                ("Settings", sidebar_item_icon("settings")),
                sidebar_item_icon("layout-dashboard"),
            ),
            rx.text(text, size="3", weight="regular"),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            style={
                "_hover": {
                    "background_color": rx.cond(
                        active,
                        styles.accent_bg_color,
                        styles.gray_bg_color,
                    ),
                    "color": rx.cond(
                        active,
                        styles.accent_text_color,
                        styles.text_color,
                    ),
                    "opacity": "1",
                },
                "opacity": rx.cond(
                    active,
                    "1",
                    "0.95",
                ),
            },
            align="center",
            border_radius=styles.border_radius,
            width="100%",
            spacing="2",
            padding="0.35em",
        ),
        underline="none",
        href=url,
        width="100%",
    )


def sidebar() -> rx.Component:
    """El Sidebar.

    Returns:
        El componente del Sidebar.

    """
    # Obtener todas las páginas decoradas y añadirlas al Sidebar.
    from reflex.page import get_decorated_pages

    # Las rutas de las páginas ordenadas.
    ordered_page_routes = [
        "/",
        "/about",
        "/settings",
    ]
    # Obtener las páginas decoradas.
    pages = get_decorated_pages()

    # Incluir todas las páginas incluso si no están en ordered_page_routes.
    ordered_pages = sorted(
        pages,
        key=lambda page: (
            ordered_page_routes.index(page["route"])
            if page["route"] in ordered_page_routes
            else len(ordered_page_routes)
        ),
    )

    return rx.flex(
        rx.vstack(
            
            rx.vstack(
                *[
                    sidebar_item(
                        text=page.get("title", page["route"].strip("/").capitalize()),
                        url=page["route"],
                    )
                    for page in ordered_pages
                ],
                spacing="1",
                width="100%",
            ),
            rx.spacer(),
            justify="end",
            align="end",
            width=styles.sidebar_content_width,
            height="100dvh",
            padding="1em",
        ),
        display=["none", "none", "none", "none", "none", "flex"],
        max_width=styles.sidebar_width,
        width="auto",
        height="100%",
        position="sticky",
        justify="end",
        top="0px",
        left="0px",
        flex="1",
        bg=rx.color("red", 2),
    )
