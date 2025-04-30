from typing import List
from sqlmodel import Session
from ..repository.database import select_all_entregables, engine
from ..models.entregable_model import Entregable
import reflex as rx

class TableEntregablesState(rx.State):
    """Estado para manejar la tabla de Entregables."""

    entregables: List[Entregable] = []

    search_value: str = ""
    sort_value: str = "nombre_entregable"  # Columna por defecto para ordenar
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 12  # Número de filas por página

    @rx.var(cache=True)
    def filtered_sorted_entregables(self) -> List[Entregable]:
        entregables = self.entregables

        # Filtrar elementos basados en el valor de ordenación seleccionado
        if self.sort_value:
            entregables = sorted(
                entregables,
                key=lambda item: str(getattr(item, self.sort_value)).lower(),
                reverse=self.sort_reverse,
            )

        # Filtrar elementos basados en el valor de búsqueda
        if self.search_value:
            search_value = self.search_value.lower()
            entregables = [
                item
                for item in entregables
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "nombre_entregable",
                        "codigo_proyecto",
                        "disciplina",
                        "clasificacion_entregable",
                        "tipo_entregable",
                        "codigo_entregable",
                        "total_hh",
                    ]
                )
            ]

        return entregables

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 0
        )

    # Obtener la página actual
    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[Entregable]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_entregables[start_index:end_index]

    # Navegación entre páginas
    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    # Cargar datos de la base de datos
    def load_entries(self):
        try:
            datos_db = select_all_entregables()  # Obtiene los datos desde la base de datos
            print(f"Datos obtenidos: {datos_db}")  # Debugging

            self.entregables = datos_db
            self.total_items = len(self.entregables)
            print(f"Se cargaron {self.total_items} registros desde la base de datos.")

        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {e}")

    # Cambiar el orden de clasificación
    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()