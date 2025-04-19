from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# waiter
class WaiterInput(BaseModel):
    name: str
    upi_id: str

class WaiterOutput(BaseModel):
    id: int
    name: str
    upi_id: str

    class Config:
        orm_mode = True

# bill
class BillInput(BaseModel):
    table_no: int
    amount: int
    waiter_id: int

class BillOutput(BaseModel):
    id: int
    table_no: int
    amount: int
    waiter_id: int
    status: str

    class Config:
        orm_mode = True

# transaction
class TransactionInput(BaseModel):
    bill_id: int
    waiter_id: int
    tip_amount: int
    total_amount: int

class TransactionOutput(BaseModel):
    id: int
    bill_id: int
    waiter_id: int
    tip_amount: int
    total_amount: int
    timestamp: datetime
    status: str
    transaction_id: str

    class Config:
        orm_mode = True
        
# tip
class TipOut(BaseModel):
    id: int
    waiter_id: int
    total_tip: int
    settled_at: datetime
    transaction_id: str