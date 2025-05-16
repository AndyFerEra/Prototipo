from sqlmodel import SQLModel, Field

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
    
