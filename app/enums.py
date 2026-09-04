from enum import Enum


class ItemStatus(str, Enum):
    available = 'available'
    requested = 'requested'
    checked_out = 'checked_out'
    maintenance = 'maintenance'
    retired = 'retired'

class ItemCondition(str, Enum):
    excellent = "excellent"
    good = "good"
    fair = "fair"
    damaged = "damaged"

class LoanStatus(str, Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    cancelled = 'cancelled'
    checked_out = 'checked_out'
    returned = 'returned'
    overdue = 'overdue'

class LoanEventType(str, Enum):
    created = "created"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
    checked_out = "checked_out"
    returned = "returned"
    overdue = "overdue"

class Role(str, Enum):
    member = 'member'
    staff = 'staff'
    admin = 'admin'