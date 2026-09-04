from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import Annotated, cast
from .database import get_db
from .auth import get_current_user
from .models import User, LoanRequest, Item, LoanEvent
from .enums import Role, LoanStatus, ItemStatus, LoanEventType
from datetime import datetime, date

def approve_request(request_id: int, db: Session, user: User, decision_reason: str | None):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    loan_req = db.get(LoanRequest, request_id)
    if loan_req is None:
        raise HTTPException(status_code=404, detail="Loan request does not exist")
    if cast(LoanStatus, loan_req.status) != LoanStatus.pending:
        raise HTTPException(status_code=409, detail="Only pending requests can be approved")
    item = db.get(Item, loan_req.item_id)
    if cast(ItemStatus, item.status) != ItemStatus.available:
        raise HTTPException(status_code=409, detail="Item is no longer available")
    
    setattr(loan_req, "status", LoanStatus.approved)
    setattr(loan_req, "reviewed_by_id", user.id)
    setattr(loan_req, "decision_reason", decision_reason)

    setattr(item, "status", ItemStatus.requested)

    db.flush()

    new_loan_event = LoanEvent(loan_request_id=loan_req.id, actor_user_id=user.id, event_type=LoanEventType.approved, old_status=LoanStatus.pending, new_status=LoanStatus.approved, note=decision_reason)

    db.add(new_loan_event)
    db.commit()
    return loan_req

def reject_request(request_id: int, db: Session, user: User, decision_reason: str | None):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    loan_req = db.get(LoanRequest, request_id)
    if loan_req is None:
        raise HTTPException(status_code=404, detail="Loan request does not exist")
    if cast(LoanStatus, loan_req.status) != LoanStatus.pending:
        raise HTTPException(status_code=409, detail="Only pending requests can be rejected")

    setattr(loan_req, "decision_reason", decision_reason)
    setattr(loan_req, "status", LoanStatus.rejected)
    setattr(loan_req, "reviewed_by_id", user.id)

    new_loan_event = LoanEvent(loan_request_id=loan_req.id, actor_user_id=user.id, event_type=LoanEventType.rejected,old_status=LoanStatus.pending, new_status=LoanStatus.rejected, note=decision_reason)

    db.add(new_loan_event)
    db.commit()
    return loan_req

def request_checkout(user: User, db: Session, request_id: int, decision_reason: str | None):
    if cast(Role, user.role) == Role.member:
            raise HTTPException(status_code=403, detail="Not Authorized")
    loan_req = db.get(LoanRequest, request_id)
    if loan_req is None:
            raise HTTPException(status_code=404, detail="Loan request does not exist")
    if cast(LoanStatus, loan_req.status) != LoanStatus.approved:
            raise HTTPException(status_code=409, detail="Only approved requests can be checked out")
    
    item = db.get(Item, loan_req.item_id)
    if cast(ItemStatus, item.status) != ItemStatus.requested:
         raise HTTPException(status_code=409, detail="Item is not reserved")

    checkout_time = datetime.now()

    setattr(loan_req, "status", LoanStatus.checked_out)
    setattr(loan_req, "reviewed_by_id", user.id)
    setattr(loan_req, "decision_reason", decision_reason)
    setattr(loan_req, "checked_out_at", checkout_time)

    setattr(item, "status", ItemStatus.checked_out)

    new_loan_event = LoanEvent(loan_request_id=loan_req.id, actor_user_id=user.id, event_type=LoanEventType.checked_out,old_status=LoanStatus.approved, new_status=LoanStatus.checked_out, note=decision_reason)

    db.add(new_loan_event)
    db.commit()
    return loan_req

def return_loan(db: Session, user: User, request_id: int, item_condition, decision_reason: str | None):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    loan_req = db.get(LoanRequest, request_id)
    if loan_req is None:
            raise HTTPException(status_code=404, detail="Loan request does not exist")
    if cast(LoanStatus, loan_req.status) not in [LoanStatus.checked_out, LoanStatus.overdue]:
            raise HTTPException(status_code=409, detail="Only checked out or overdue requests can be returned")

    return_time = datetime.now()

    old_status = loan_req.status

    setattr(loan_req, "status", LoanStatus.returned)
    setattr(loan_req, "return_condition", item_condition)
    setattr(loan_req, "returned_at", return_time)
    setattr(loan_req, "reviewed_by_id", user.id)
    setattr(loan_req, "decision_reason", decision_reason)

    item = db.get(Item, loan_req.item_id)

    setattr(item, "status", ItemStatus.available)
    setattr(item, "condition", item_condition)

    new_loan_event = LoanEvent(loan_request_id=loan_req.id, actor_user_id=user.id, event_type=LoanEventType.returned, old_status=old_status, new_status=LoanStatus.returned, note=decision_reason)

    db.add(new_loan_event)
    db.commit()
    return loan_req

def overdue_loans(db: Session, user: User):
    if cast(Role, user.role) == Role.member:
        raise HTTPException(status_code=403, detail="Not Authorized")
    today = date.today()
    loans = db.scalars(select(LoanRequest).where(LoanRequest.status==LoanStatus.checked_out, LoanRequest.requested_return_date < today)).all()
    for loan_req in loans:
        setattr(loan_req, "status", LoanStatus.overdue)
    db.commit()
    result = db.scalars(select(LoanRequest).where(LoanRequest.status == LoanStatus.overdue)).all()
    return result