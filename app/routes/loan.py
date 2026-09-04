from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from typing import Annotated, cast
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Item, LoanRequest, LoanEvent
from ..enums import Role, ItemStatus, LoanStatus, LoanEventType
from ..schemas import LoanRequestIn, LoanRequestOut
from datetime import date

router = APIRouter(tags=['loans'])

dbSession = Annotated[Session, Depends(get_db)]

@router.post('/items/{id}/requests', response_model=LoanRequestOut)
def loan_request(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)], loan_detail: LoanRequestIn):
    if cast(Role, user.role) != Role.member:
        raise HTTPException(status_code=403, detail='Not Authorized')
    item = db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail='Item does not exist')
    existing_request = db.scalar(select(LoanRequest).where(LoanRequest.borrower_id==user.id, LoanRequest.item_id==item.id, LoanRequest.status==LoanStatus.pending))
    if existing_request:
        raise HTTPException(status_code=409, detail='You already have a pending request for this item')
    if cast(ItemStatus, item.status) != ItemStatus.available:
        raise HTTPException(status_code=409, detail='Item is not available for request')
    requested_return_date = loan_detail.requested_return_date
    if requested_return_date <= date.today():
        raise HTTPException(status_code=400, detail='Requested return date must be in the future')
    new_loan_request = LoanRequest(item_id=item.id, borrower_id=user.id, requested_return_date=requested_return_date)

    db.add(new_loan_request)
    db.flush()

    new_loan_event = LoanEvent(loan_request_id=new_loan_request.id, actor_user_id=user.id, event_type=LoanEventType.created, new_status=LoanStatus.pending)

    db.add(new_loan_event)
    db.commit()
    db.refresh(new_loan_request)
    return new_loan_request

@router.get('/requests/mine', response_model=list[LoanRequestOut])
def loan_get(user: Annotated[User, Depends(get_current_user)]):
    if cast(Role, user.role) != Role.member:
            raise HTTPException(status_code=403, detail='Not Authorized')
    return user.loan_requests


@router.patch('/requests/{id}/cancel')
def loan_cancel(id: int, user: Annotated[User, Depends(get_current_user)], db: dbSession):
    if cast(Role, user.role) != Role.member:
                raise HTTPException(status_code=403, detail='Not Authorized')
    user_req = db.scalar(select(LoanRequest).where(LoanRequest.borrower_id == user.id, LoanRequest.id==id))
    if user_req is None:
        raise HTTPException(status_code=404, detail='Loan request does not exist')
    if cast(LoanStatus, user_req.status) != LoanStatus.pending:
         raise HTTPException(status_code=409, detail="Only pending requests can be cancelled")
    new_loan_event = LoanEvent(loan_request_id=user_req.id, actor_user_id=user.id, event_type=LoanEventType.cancelled, new_status=LoanStatus.cancelled, old_status=LoanStatus.pending)
    setattr(user_req, 'status', LoanStatus.cancelled)
    db.add(new_loan_event)
    db.commit()