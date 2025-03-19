from sqlmodel import create_engine, Session, select,SQLModel
from ..models.excel_data import ExcelData,Reglas,Proyectos,Entregables,Entregable


# Construir la URL de conexión a la base de datos
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/pro_bisa"
engine = create_engine(DATABASE_URL)

# Crear tablas si no existen
SQLModel.metadata.create_all(engine)


# Crear una sesión para interactuar con la base de datos
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
        
