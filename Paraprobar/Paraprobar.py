"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx

# Importaciones CORRECTAS:
from Paraprobar import styles  # ¡Usa el nombre del paquete!
from Paraprobar.pages import *
from Paraprobar.repository.database import init_db

init_db()

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
