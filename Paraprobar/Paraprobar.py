"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx

from . import styles
from .pages import *

from .repository.database import init_db

init_db()

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
