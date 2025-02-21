"""Componente Navbar para la aplicación."""

import reflex as rx

from .. import styles

#funcion para dar estilos a los iconos del sidebar
def menu_item_icon(icon: str) -> rx.Component:
    return rx.icon(icon, size=20)


def menu_item(text: str, url: str) -> rx.Component:
    """Elemento del menú.

    Args:
        text: El texto del elemento.
        url: La URL del elemento.

    Returns:
        rx.Component:  El componente del elemento del menú.

    """
    # Cuando el item este activo.
    active = (rx.State.router.page.path == url.lower()) | (
        (rx.State.router.page.path == "/") & text == "Overview"
    )

    return rx.link(
        rx.hstack(
            rx.match(
                text,
                ("Listado de entregables", menu_item_icon("layout-dashboard")),
                ("About", menu_item_icon("book-open")),
                ("Settings", menu_item_icon("settings")),
                menu_item_icon("layout-dashboard"),
            ),
            rx.text(text, size="4", weight="regular"),
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

# El final del sidebar
def navbar_footer() -> rx.Component:
    """Pie de página del Navbar.

    Returns:
        El componente del pie de página del Navbar.

    """
    return rx.hstack(
        rx.link(
            rx.text("Docs", size="3"),
            href="https://reflex.dev/docs/getting-started/introduction/",
            color_scheme="gray",
            underline="none",
        ),
        rx.link(
            rx.text("Blog", size="3"),
            href="https://reflex.dev/blog/",
            color_scheme="gray",
            underline="none",
        ),
        rx.spacer(),
        rx.color_mode.button(style={"opacity": "0.8", "scale": "0.95"}),
        justify="start",
        align="center",
        width="100%",
        padding="0.35em",
    )


def menu_button() -> rx.Component:
    # Consigue todas las páginas decoradas y añádelas al menú.
    from reflex.page import get_decorated_pages

    # Las rutas de las paginas ordenadas
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
    #Da la funcionalidad al sidebar
    return rx.drawer.root(
        rx.drawer.trigger(#Permite sobreponer el sidebar
            rx.icon("align-justify"),
        ),
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        rx.spacer(),
                        rx.drawer.close(rx.icon(tag="x")),
                        justify="start",
                        width="100%",
                    ),
                    rx.divider(),
                    *[#Añade las paginas al sidebar
                        menu_item(
                            text=page.get(
                                "title", page["route"].strip("/").capitalize()
                            ),
                            url=page["route"],
                        )
                        for page in ordered_pages
                    ],
                    rx.spacer(),
                    navbar_footer(),
                    spacing="4",
                    width="100%",
                ),
                top="auto",
                left="auto",
                height="100%",
                width="20em",
                padding="1em",
                bg=rx.color("gray", 1),
            ),
            width="100%",
        ),
        direction="right",
    )


def navbar() -> rx.Component:
    """El Navbar.

    Returns:
        El componente del Navbar.

    """
    return rx.el.nav(
        rx.hstack(
            
            menu_button(),
            # El logo.
            rx.color_mode_cond(
                rx.image(src="/reflex_black.svg", height="1em"),
                rx.image(src="/reflex_white.svg", height="1em"),
            ),
            align="center",
            width="100%",
            padding_y="1.25em",
            padding_x=["1em", "1em", "2em"],
        ),
        display=["block", "block", "block", "block", "block", "none"],
        position="sticky",
        background_color=rx.color("gray", 1),
        top="0px",
        z_index="5",
        border_bottom=styles.border,
    )
