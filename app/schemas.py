from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from .enums import ItemCondition, LoanStatus


class UserIn(BaseModel):
    full_name: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=4, max_length=16)
    email: EmailStr

class UserOut(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    id: int
    is_active: bool
    created_at: datetime

class CategoryIn(BaseModel):
    name: str
    description: str

class CategoryOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    category: str
    asset_code: str = Field(min_length=4)
    description: str | None = None
    condition: ItemCondition
    purchase_date: date
    notes: str | None = None

class ItemEdit(BaseModel):
    name: str | None = None
    category_id: int | None = None
    description: str | None = None
    condition: ItemCondition | None = None
    purchase_date: date | None = None
    notes: str | None = None

class ItemOut(BaseModel):
    id: int
    name: str
    category_id: int
    asset_code: str
    description: str | None
    status: str
    condition: str
    purchase_date: date
    notes: str | None
    created_at: datetime

class LoanRequestIn(BaseModel):
    requested_return_date: date

class LoanRequestOut(BaseModel):
    id: int
    item_id: int
    borrower_id: int
    reviewed_by_id: int | None
    requested_return_date: date
    status: LoanStatus
    decision_reason: str | None
    checked_out_at: datetime | None
    returned_at: datetime | None
    return_condition: str | None
    created_at: datetime

class LoanReturn(BaseModel):
    item_condition: ItemCondition
    decision_reason: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str