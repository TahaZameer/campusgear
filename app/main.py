from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from .database import Base, engine
from .routes import authentication, category, health, item, loan, staff

app = FastAPI()

app.include_router(authentication.router)
app.include_router(category.router)
app.include_router(item.router)
app.include_router(loan.router)
app.include_router(staff.router)
app.include_router(health.router)

Base.metadata.create_all(bind=engine)