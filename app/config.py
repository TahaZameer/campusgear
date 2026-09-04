import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["DB_URL"]

SECRET_KEY = os.environ["SECRET_KEY"]

ALGORITHM = os.environ["ALGORITHM"]