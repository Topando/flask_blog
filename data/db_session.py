import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return
    # postgresql+psycopg2://user:password@hostname/database_name
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(
        "postgresql+psycopg2://tkrpujjplpturj:958a136f1723758f54029507c0575079f6972238217e5605ad1ac6a23a2231df@ec2-54-236-137-173.compute-1.amazonaws.com/dd48pmpea10n0l",
        echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
