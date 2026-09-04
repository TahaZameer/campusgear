from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URL = os.environ["DB_URL"]

engine = create_engine(DB_URL)

LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    with LocalSession() as db:
        yield db