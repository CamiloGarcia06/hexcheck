from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_session_factory(db_path: str) -> sessionmaker:
    return sessionmaker(bind=create_engine(f'sqlite:///{db_path}'))
