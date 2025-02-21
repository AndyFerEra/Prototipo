from sqlmodel import SQLModel, Field
import reflex as rx
from typing import Optional

class User(rx.Model, table=True):
    id: Optional [int] = Field(default=None, primary_key=True)
    nombre: str
    edad: int
    email: str

class ExcelData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str
    edad: int
    email: str
