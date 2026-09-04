from fastapi import APIRouter, Depends, Body
from fastapi.exceptions import HTTPException
from typing import Annotated, cast
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Category, User
from ..database import get_db
from ..schemas import CategoryIn, CategoryOut
from ..auth import get_current_user
from ..enums import Role

router = APIRouter(prefix='/categories', tags=['categories'])

dbSession = Annotated[Session, Depends(get_db)]

@router.post('', response_model=CategoryOut)
def create_category(user: Annotated[User, Depends(get_current_user)], db: dbSession, category: Annotated[CategoryIn, Body()]):
    if cast(Role, user.role) != Role.admin:
        raise HTTPException(status_code=403, detail="Not Authorized")
    category_name = str.lower(category.name)
    check = db.scalar(select(Category).where(Category.name == category_name))
    if check:
        raise HTTPException(status_code=409, detail='Category already exists')
    new_category = Category(name=category_name, description=category.description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get('', response_model=list[CategoryOut])
def list_categories(user: Annotated[User, Depends(get_current_user)], db: dbSession):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    categories = db.scalars(select(Category)).all()
    return categories