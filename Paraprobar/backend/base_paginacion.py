import reflex as rx

class PaginacionBase(rx.State):
    offset: int = 0
    limit: int = 10
    sort_reverse: bool = False
    total_items: int = 0

    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (1 if self.total_items % self.limit else 0)

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def load_entries(self):
        pass  # implementado en hijos
