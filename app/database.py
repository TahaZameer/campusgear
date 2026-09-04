from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DB_URL

engine = create_engine(DB_URL)

LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    with LocalSession() as db:
        yield db