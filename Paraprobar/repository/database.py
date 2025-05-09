from sqlmodel import asc, create_engine, Session, select,SQLModel
from ..models.excel_data import ExcelData,Reglas,Proyectos,Entregables,vistaentregablesproyectos
from urllib.parse import quote_plus


# Codificar la contraseña (por el carácter @)
password = "12345"
encoded_password = quote_plus(password)

# Cadena de conexión
DATABASE_URL = rf"mssql+pyodbc://sa:{encoded_password}@DESKTOP-L84HKA8\BISA/pro_bisa?driver=ODBC+Driver+17+for+SQL+Server"
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
    
def lafeeeeeeeeeeeee():
    with Session(engine) as session:
        statement = select(vistaentregablesproyectos)
        results = session.exec(statement)
        return results.all()

def get_unique_values_by_column(column_name):
    """Obtiene una lista de valores únicos de la base de datos filtrados por una columna específica."""
    with Session(engine) as session:
        statement = (
            select(getattr(vistaentregablesproyectos, column_name))
            .distinct()  # Selecciona solo valores únicos
        )
        results = session.execute(statement)
        return [row[0] for row in results]

    
