from sqlmodel import SQLModel, Field
from typing import Optional


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
    
