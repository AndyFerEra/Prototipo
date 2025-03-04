from sqlmodel import SQLModel, Field
import reflex as rx
from typing import Optional

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
    id: int = Field(default=None, primary_key=True)
    codigo_proyecto: str
    orden_trabajo: str
    cliente: int
    nombre_proyecto: str
    sector:str
    etapa_ingenieria: str
    pais: str
    año: str
    estado: str
    cant_entrg_prop: str
    hh_propuesta: str
    presu_costo_directo: str
    presu_total_sindescu: str
    ratiohh_entrg_propuesta: str #este es generado al dividir hh_propuesta/cant_entrg_prop
    ratiocd_entreg_pro: str  #al dividir presu_costo_directo/cant_entrg_prop
    margenes_propuesta: str
    cantidad_entregables_cierre: str
    hh_cierre: str
    venta_cierre: str
    ratiohh_entrg_cierre: str #al dividir hh_cierre/cantidad_entregables_cierre
    ratiocosto_entrg_cierre: str # al dividir venta_cierre/cantidad_entregables_cierre
    margenes_cierre: str
    
    
    
