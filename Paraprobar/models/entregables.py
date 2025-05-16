from sqlmodel import SQLModel, Field
from typing import Optional


class Entregables(SQLModel, table=True):
    __tablename__ = "entregables"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_proyecto_entregables: str = Field(max_length=100, index=True)
    disciplina_entregables: str = Field(max_length=50, index=True)
    clasificacion_entregable: Optional[str] = Field(default=None, max_length=50)  # Asegura compatibilidad
    tipo_entregable_entre: str = Field(max_length=50, index=True)
    codigo_entregable: str = Field(max_length=255, index=True)  # Ajustado para permitir más caracteres
    nombre_entregable: str = Field(max_length=255, index=True)  # Ajustado también aquí
    total_hh: Optional[float] = Field(default=None)  # Valor opcional como en la primera definición
    enlace_pdf: Optional[str] = Field(default=None, max_length=500)  # Permite enlaces largos y opcionales
    enlace_nativo: Optional[str] = Field(default=None, max_length=500)  # También opcional y largo
    
    
class vistaentregablesproyectos(SQLModel, table=True):
    __tablename__ = "vista_entregables_proyectos"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_proyecto_entregables: str
    disciplina_entregables: str
    tipo_entregable_entre: str
    codigo_entregable: str
    nombre_entregable: str
    total_hh: Optional[int]
    enlace_pdf: str
    enlace_nativo: str
    cliente: str
    nombre_proyecto: str