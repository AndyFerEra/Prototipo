from sqlmodel import SQLModel, Field
import reflex as rx
from typing import Optional
from datetime import datetime

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

class MetadatosPDF(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    archivo: str
    titulo: Optional[str] = None
    autor: Optional[str] = None
    asunto: Optional[str] = None
    palabras_clave: Optional[str] = None
    creador: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_modificacion: Optional[str] = None
    numero_paginas: Optional[int] = None