from sqlmodel import create_engine, Session, select
from ..models.excel_data import User

DATABASE_URL = "mysql+mysqlconnector://root:@localhost/pro_bisa"
engine = create_engine(DATABASE_URL)

def select_all():
    engine.connect()
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement)
        return results.fetchall()