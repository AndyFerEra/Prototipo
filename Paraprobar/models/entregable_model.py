from sqlmodel import SQLModel, Field

class Entregable(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_entregable: str
    codigo_proyecto: str
    disciplina: str
    clasificacion_entregable: str
    tipo_entregable: str
    codigo_entregable: str
    total_hh: float