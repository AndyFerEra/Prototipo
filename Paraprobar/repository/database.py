from sqlmodel import create_engine, Session, select,SQLModel
from sqlmodel import select, Session, func, or_, asc, desc
from ..models.excel_data import Reglas,Proyectos,Entregables
from ..models.entregable_model import Entregable
from supabase import create_client, Client
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlmodel import create_engine
import os

load_dotenv()
# Leer las variables de entorno
USER_ENV = os.getenv("USER_ENV")
PASS_ENV = os.getenv("PASS_ENV")
DATABASE_ENV = os.getenv("DATABASE_ENV")


# Crear cliente de Supabase
supabase: Client = create_client("https://arqzlruygpuwmyosqerh.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFycXpscnV5Z3B1d215b3NxZXJoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzAxMDY2MywiZXhwIjoyMDU4NTg2NjYzfQ.j7uQFzd7tgQLJQLGLOuVGdyirGiCaVk1Jp4Phw0H2lY")

# Construir la URL de conexión a la base de datos
#DATABASE_URL = f"mysql+mysqlconnector://{USER_ENV}:{PASS_ENV}@localhost/{DATABASE_ENV}"
# Codificar la contraseña (por el carácter @)
password = "uncp@2024"
encoded_password = quote_plus(password)

# Cadena de conexión
DATABASE_URL = f"mssql+pyodbc://sa:{encoded_password}@DESKTOP-FJD64AH/proy_bisa?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)

# Inicializar la base de datos
def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# Crear una sesión
def get_session():
    try:
        return Session(engine)
    except Exception as e:
        print(f"Error al crear la sesión: {e}")
        return None
# Obtener todos los registros de la tabla "Entregable"
def select_all_entregables():
    with Session(engine) as session:
        statement = select(Entregable)
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
    
def get_unique_codigo_proyectos():
    """Obtiene una lista de códigos de proyecto únicos de la base de datos."""
    with Session(engine) as session:
        statement = select(Entregables.disciplina_entregables).distinct()  # Selecciona solo valores únicos
        results = session.execute(statement)
        return [row[0] for row in results]
    

def get_unique_values_by_column(column_name):
    """Obtiene una lista de valores únicos de la base de datos filtrados por una columna específica."""
    with Session(engine) as session:
        statement = (
            select(getattr(Entregables, column_name))
            .distinct()  # Selecciona solo valores únicos
        )
        results = session.execute(statement)
        return [row[0] for row in results]
    
def select_entregables_con_proyectos():
    with Session(engine) as session:
        statement = (
            select(
                Entregables.codigo_proyecto_entregables,
                Entregables.disciplina_entregables,
                Entregables.tipo_entregable_entre,
                Entregables.codigo_entregable,
                Entregables.nombre_entregable,
                Entregables.total_hh,
                Entregables.enlace_pdf,
                Entregables.enlace_nativo,
                Proyectos.orden_trabajo,
                Proyectos.cliente,
                Proyectos.nombre_proyecto,
            )
            .join(Proyectos, Proyectos.codigo_proyecto == Entregables.codigo_proyecto_entregables)
        )
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