from sqlmodel import create_engine, Session, select
from ..models.excel_data import ExcelData


DATABASE_URL = "mysql+mysqlconnector://root:@localhost/pro_bisa"
engine = create_engine(DATABASE_URL)

#prueba
def select_all():
    with Session(engine) as session:
        statement = select(ExcelData)
        results = session.exec(statement)
        return results.all()
