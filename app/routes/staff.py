from typing import Annotated, cast

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..enums import LoanStatus, Role
from ..models import LoanRequest, User
from ..schemas import LoanRequestOut, LoanReturn
from ..services import (
    approve_request,
    overdue_loans,
    reject_request,
    request_checkout,
    return_loan,
)

router = APIRouter(prefix='/staff', tags=['staff'])

dbSession = Annotated[Session, Depends(get_db)]

@router.get('/requests', response_model=list[LoanRequestOut])
def get_loan_requests(db: dbSession, user: Annotated[User, Depends(get_current_user)], status: Annotated[LoanStatus, Query()], item_id: Annotated[int, Query()], borrower_id: Annotated[int, Query()]):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    statement = select(LoanRequest)
    if status is not None:
        statement = statement.where(LoanRequest.status == status)
    if item_id is not None:
        statement = statement.where(LoanRequest.item_id == item_id)
    if borrower_id is not None:
        statement = statement.where(LoanRequest.borrower_id == borrower_id)
    result = db.scalars(statement).all()
    return result

@router.patch('/requests/{id}/approve', response_model=LoanRequestOut)
def approve_loan_request(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)], decision_reason: str | None = None):
    approved_req = approve_request(db=db, user=user, request_id=id, decision_reason=decision_reason)
    return approved_req

@router.patch('/requests/{id}/reject', response_model=LoanRequestOut)
def reject_loan_request(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)], decision_reason: str | None = None):
    rejected_req = reject_request(db=db, user=user, request_id=id, decision_reason=decision_reason)
    return rejected_req

@router.patch('/requests/{id}/checkout', response_model=LoanRequestOut)
def loan_request_checkout(id: int, db: dbSession, user: Annotated[User, Depends(get_current_user)], decision_reason: str | None = None):
    checked_out_request = request_checkout(db=db, user=user, decision_reason=decision_reason, request_id=id)
    return checked_out_request

@router.patch('/requests/{id}/return', response_model=LoanRequestOut)
def loan_return(id: int, loan_details: LoanReturn, db: dbSession, user: Annotated[User, Depends(get_current_user)]):
    returned_loan = return_loan(db=db, user=user, decision_reason=loan_details.decision_reason, request_id=id, item_condition=loan_details.item_condition)
    return returned_loan

@router.get('/loans/overdue', response_model=list[LoanRequestOut])
def overdue_active_requests(db: dbSession, user: Annotated[User, Depends(get_current_user)]):
    loans = overdue_loans(db=db, user=user)
    return loans