from sqlmodel import SQLModel, Field
import reflex as rx
from typing import Optional
from datetime import datetime

class User(rx.Model, table=True):
    id: Optional [int] = Field(default=None, primary_key=True)
    nombre: str
    edad: int
    email: str

#prueba
class ExcelData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str
    edad: int
    email: str
    
#Para la tabla de reglas
class Reglas(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    perfiles: str
    disciplina: str
    codigo_disciplina: int
    tipo_entregable: str
    codigo_wbs:str
    codigo_ted: str
    ted: str
    sector: str
    etapa_ingenieria: str
    estado: str
    
#Para la tabla de proyectos
class Proyectos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_proyecto: str
    orden_trabajo: str
    cliente: str
    nombre_proyecto: str
    sector: str
    etapa_ing: str
    pais: str
    año: Optional[int] = Field(default=None)
    estado: str
    cant_entrg_prop:  Optional[int] = Field(default=None)
    hh_propuesta: Optional[float] = None
    presu_costo_directo: Optional[float] = None
    presu_total_sindescu: Optional[float] = None
    ratiohh_entrg_propuesta: Optional[float] = None 
    ratiocd_entreg_pro: Optional[float] = None  
    margenes_propuesta: Optional[float] = None
    cantidad_entregables_cierre: Optional[int] = Field(default=None)
    hh_cierre: Optional[float] = None
    venta_cierre: Optional[float] = None
    ratiohh_entrg_cierre: Optional[float] = None  
    ratiocosto_entrg_cierre: Optional[float] = None  
    margenes_cierre: Optional[float] = None

    @staticmethod
    def parse_year(year_str: str) -> int:
        return datetime.strptime(year_str, "%Y").year

#Para la tabla de Entregables
class Entregables(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_proyecto_entregables: str
    disciplina_entregables: str
    clasificacion_entregable: str
    tipo_entregable_entre: str
    codigo_entregable: str
    nombre_entregable: str
    total_hh: Optional[int] = None
    enlace_pdf: str
    enlace_nativo: str


