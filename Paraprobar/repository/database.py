from sqlmodel import create_engine, Session, select,SQLModel
from sqlmodel import select, Session, func, or_, asc, desc
from ..models.excel_data import ExcelData,Reglas,Proyectos,Entregables
from ..models.entregable_model import Entregable
from dotenv import load_dotenv
import os

load_dotenv()
# Leer las variables de entorno
USER_ENV = os.getenv("USER_ENV")
PASS_ENV = os.getenv("PASS_ENV")
DATABASE_ENV = os.getenv("DATABASE_ENV")


# Construir la URL de conexión a la base de datos
DATABASE_URL = f"mysql+mysqlconnector://{USER_ENV}:{PASS_ENV}@localhost/{DATABASE_ENV}"
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

# Obtener todos los registros de la tabla "Entregable"
def select_all_entregables():
    with Session(engine) as session:
        statement = select(Entregable)
        results = session.exec(statement)
        return results.all()
    
#prueba
def select_all():
    with Session(engine) as session:
        statement = select(ExcelData)
        results = session.exec(statement)
        return results.all()

#tabla reglas
def select_all_reglas():
    with Session(engine) as session:
        statement = select(Reglas)
        results = session.exec(statement)
        return results.all()

def select_all_proyectos():
    with Session(engine) as session:
        statement = select(Proyectos)
        results = session.exec(statement)
        return results.all()

def select_all_entregables_2():
    with Session(engine) as session:
        statement = select(Entregables)
        results = session.exec(statement)
        return results.all()
    
def get_entregables_paginados(
    search: str = "", 
    sort_field: str = None, 
    sort_desc: bool = False,
    offset: int = 0, 
    limit: int = 20
) -> tuple[list[Entregables], int]:
    """Obtiene entregables con paginación, búsqueda y ordenamiento"""
    with Session(engine) as session:
        query = select(Entregables)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                or_(
                    Entregables.nombre_entregable.ilike(search_term),
                    Entregables.codigo_entregable.ilike(search_term),
                    Entregables.codigo_proyecto_entregables.ilike(search_term),
                    Entregables.disciplina_entregables.ilike(search_term),
                    Entregables.tipo_entregable_entre.ilike(search_term)
                )
            )
        
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        
        if sort_field:
            field = getattr(Entregables, sort_field)
            query = query.order_by(desc(field) if sort_desc else asc(field))
        
        items = session.exec(query.offset(offset).limit(limit)).all()
        return items, total