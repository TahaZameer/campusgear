from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .database import Base
from .enums import ItemCondition, ItemStatus, LoanEventType, LoanStatus, Role


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, nullable=False, default=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SqlEnum(Role, name='user_role_enum'), nullable=False, default=Role.member)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now() , nullable=False)
    
    loan_requests = relationship('LoanRequest', foreign_keys='LoanRequest.borrower_id' ,back_populates='borrower')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now() , nullable=False)

    items = relationship('Item', back_populates='category')

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    asset_code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    condition = Column(SqlEnum(ItemCondition, name='item_condition_enum'), nullable=False)
    status = Column(SqlEnum(ItemStatus, name='item_status_enum'), nullable=False, default=ItemStatus.available)
    purchase_date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship('Category', back_populates='items')

    loan_requests = relationship('LoanRequest', back_populates='item')

class LoanRequest(Base):
    __tablename__ = 'loan_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.id') ,nullable=False)
    borrower_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewed_by_id = Column(Integer, ForeignKey('users.id') ,nullable=True)
    requested_return_date = Column(Date, nullable=False)
    status = Column(SqlEnum(LoanStatus, name='loan_status_enum'), nullable=False, default='pending')
    decision_reason = Column(String, nullable=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    return_condition = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    borrower = relationship('User', foreign_keys=[borrower_id], back_populates='loan_requests')

    events = relationship('LoanEvent', back_populates='request')

    item = relationship('Item', back_populates='loan_requests')

class LoanEvent(Base):
    __tablename__ = 'loan_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_request_id = Column(Integer, ForeignKey('loan_requests.id'), nullable=False)
    actor_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_type = Column(SqlEnum(LoanEventType, name='loan_event_type_enum'), nullable=False)
    old_status = Column(SqlEnum(LoanStatus, name='loan_status_enum'), nullable=True)
    new_status = Column(SqlEnum(LoanStatus, name='loan_status_enum'), nullable=False)
    note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship('LoanRequest', back_populates='events')