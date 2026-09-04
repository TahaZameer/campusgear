from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from typing import Annotated, cast
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Category, Item
from ..auth import get_current_user
from ..schemas import ItemIn, ItemOut, ItemEdit
from ..enums import Role, ItemStatus, ItemCondition

router = APIRouter(prefix='/items', tags=['items'])

dbSession = Annotated[Session, Depends(get_db)]

@router.post('/', response_model=ItemOut)
def create_item(user: Annotated[User, Depends(get_current_user)], item: ItemIn, db: dbSession):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    category = db.scalar(select(Category).where(Category.name == item.category))
    if category is None:
        raise HTTPException(status_code=404, detail='Category does not exist')
    item_check = db.scalar(select(Item).where(Item.asset_code == item.asset_code))
    if item_check:
        raise HTTPException(status_code=409, detail='Asset code already exists')
    new_item = Item(category_id=category.id, name=item.name, asset_code=item.asset_code, description=item.description, condition=item.condition, purchase_date=item.purchase_date, notes=item.notes)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get('/', response_model=list[ItemOut])
def get_all_items(db: dbSession, category_id: Annotated[int | None, Query()] = None, status: Annotated[ItemStatus | None, Query()] = None, search: Annotated[str | None, Query()] = None):
    statement = select(Item)
    if category_id is not None:
        statement = statement.where(Item.category_id == category_id)
    if search is not None:
        statement = statement.where(or_(Item.name.ilike(f"%{search}%"), Item.description.ilike(f"%{search}%")))
    if status is not None:
        statement = statement.where(Item.status == status)
    items = db.scalars(statement).all()
    return items

@router.get('/{id}', response_model=ItemOut)
def get_item(id: int, db: dbSession):
    item = db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail='Item does not exist')
    return item

@router.patch('/{id}', response_model=ItemOut)
def edit_item(id: int, db: dbSession, to_edit: ItemEdit, user: Annotated[User, Depends(get_current_user)]):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    if to_edit.category_id is not None:
        category = db.get(Category, to_edit.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail='Category does not exist')
    updates = to_edit.model_dump(exclude_unset=True)
    item = db.scalar(select(Item).where(Item.id == id))
    if item is None:
        raise HTTPException(status_code=404, detail='Item does not exist')
    for field, value in updates.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete('/{id}')
def delete_item(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)]):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    item = db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail='Item does not exist')
    if cast(ItemStatus, item.status) != ItemStatus.available:
        raise HTTPException(status_code=409, detail='Item cannot be deleted unless it is available')

    setattr(item, "status", ItemStatus.retired)
    
    db.commit()

@router.get('/{id}/history')
def item_history(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)]):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    item = db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item does not exist")
    loan_history = item.loan_requests
    return loan_history