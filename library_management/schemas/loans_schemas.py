from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class LoanStatus(str, Enum):
    ACTIVE = 'active'
    RETURNED = 'returned'


class LoanSchema(BaseModel):
    book_isbn: str


class LoanPublic(BaseModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    returned_at: datetime | None = None
    status: LoanStatus

    model_config = ConfigDict(from_attributes=True)


class LoanList(BaseModel):
    loans: list['LoanPublic']
