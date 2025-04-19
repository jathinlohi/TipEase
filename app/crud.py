from models import Waiter, Bill, Transaction, TipSettlement
import schemas, utils
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session 
from sqlalchemy import func
from datetime import datetime
from typing import Optional

# to create waiter
def create_waiter(
        db: Session, 
        waiter: schemas.WaiterInput 
):
    db_waiter = Waiter(name=waiter.name, upi_id=waiter.upi_id)
    db.add(db_waiter)
    db.commit()
    db.refresh(db_waiter)
    return db_waiter

# to get waiter using id
def get_waiter_by_id(
        db: Session,
        id: int
):
    return db.query(Waiter).filter(Waiter.id==id).first()

# to get waiter using name 
def get_waiter_by_name(
        db: Session,
        name: str
):
    return db.query(Waiter).filter(Waiter.name==name).first()

# to create bill
def create_bill(
        db: Session,
        bill: schemas.BillInput
):
    db_bill= Bill(table_no= bill.table_no, amount= bill.amount, waiter_id= bill.waiter_id)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# to get bill using id
def get_bill(
        db: Session,
        id: int
):
    return db.query(Bill).filter(Bill.id==id).first()

# to record a transaction
def create_transaction(
        db: Session,
        transaction: schemas.TransactionInput
):
    db_transaction= Transaction(bill_id=transaction.bill_id, waiter_id=transaction.waiter_id, tip_amount=transaction.tip_amount, total_amount= transaction.total_amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# to get transaction by id
def get_transaction_by_id(
        db:Session,
        id: int
):
    return db.query(Transaction).filter(Transaction.id==id).first()

# to mark bill as paid
def mark_bill_as_paid(
        db:Session,
        bill_id: int,
        transaction_id: str
):
    transaction=db.query(Transaction).filter(Transaction.bill_id==bill_id).first()
    bill=db.query(Bill).filter(Bill.id==bill_id).first()

    if bill and transaction:
        bill.status='paid'
        transaction.status='success'
        transaction.transaction_id= transaction_id
        db.commit()
        db.refresh(transaction)
        db.refresh(bill)
        return bill, transaction
    return None, None

# to get settled tips per water using id
def get_tip_settlement_by_waiterid(
        db:Session,
        waiter_id:int
):
    return db.query(TipSettlement).filter(TipSettlement.waiter_id==waiter_id).all()

# to settle tip per waiter using id
def settle_tips_for_waiter(db: Session, waiter_id: int):
    # Get all transactions for the given waiter where the tip is not yet settled
    unsettled_transactions = db.query(Transaction).filter(
        Transaction.waiter_id == waiter_id,
        Transaction.is_settled == False
    ).all()

    if not unsettled_transactions:
        return {"message": "No unsettled tips found for this waiter."}

    total_tips = sum(tx.tip_amount for tx in unsettled_transactions)

    # Mark each transaction as settled
    for tx in unsettled_transactions:
        tx.is_settled = True

    # Create a tip settlement entry for the waiter
    settlement = TipSettlement(
        waiter_id=waiter_id,
        total_tips=total_tips,
        settled_at= datetime.utcnow()
    )
    db.add(settlement)

    db.commit()  # Make sure to commit the transaction to the database
    db.refresh(settlement)

    return {
        "message": "Tips settled successfully",
        "settlement": {
            "waiter_id": settlement.waiter_id,
            "total_tips": settlement.total_tips,
            "settled_at": settlement.settled_at
        }
    }

# to create the qr code for customer
def create_bill_qr(db: Session, bill: schemas.BillInput):
    db_bill = Bill(waiter_id=bill.waiter_id, amount=bill.amount, table_no=bill.table_no)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    data = {
        'waiter_id': db_bill.waiter_id,
        'amount': db_bill.amount,
        'table_no': db_bill.table_no
    }

    qr_code_base64 = utils.generate_qr_code_base64(data)

    # Return the QR code as base64 string
    return {"qr_code_base64": qr_code_base64}

