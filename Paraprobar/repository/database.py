from sqlmodel import create_engine, Session, select,SQLModel
from sqlalchemy.sql import text
from ..models.excel_data import ExcelData,Reglas,Proyectos,Entregables,vistaentregablesproyectos


DATABASE_URL = "mysql+mysqlconnector://root:@localhost/pro_bisa"
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

    
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