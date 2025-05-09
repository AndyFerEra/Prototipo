from Paraprobar.backend.base_paginacion import PaginacionBase
from models import Proyectos  # Asegúrate de importar tu modelo

class ProyectosState(PaginacionBase):
    filtered_sorted_items_proyectos: list[Proyectos] = []

    def load_entries(self):
        # Aquí defines cómo cargar y filtrar los proyectos desde la base de datos o fuente
        self.filtered_sorted_items_proyectos = sorted(
            self.filtered_sorted_items_proyectos,
            key=lambda x: x.algun_atributo,  # reemplaza con el campo real
            reverse=self.sort_reverse,
        )
        self.total_items = len(self.filtered_sorted_items_proyectos)

    def get_current_page_proyectos(self) -> list[Proyectos]:
        start = self.offset
        end = start + self.limit
        return self.filtered_sorted_items_proyectos[start:end]
