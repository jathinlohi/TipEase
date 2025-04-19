from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base() 

class Waiter(Base):
    __tablename__='waiters'

    id = Column(Integer, primary_key= True)
    name = Column(String, nullable= False, index= True)
    upi_id = Column(String, nullable= False)

    bills= relationship('Bill', back_populates='waiter')
    transactions= relationship('Transaction', back_populates='waiter')
    tip_settlements = relationship('TipSettlement', back_populates='waiter')

class Bill(Base):
    __tablename__='bills'

    id = Column(Integer, primary_key= True)
    table_no= Column(Integer, nullable= False)
    amount= Column(Integer, nullable= False)
    waiter_id= Column(Integer, ForeignKey('waiters.id'),nullable= False)
    status= Column(String, default='unpaid')

    waiter= relationship('Waiter', back_populates= 'bills')
    transaction = relationship('Transaction', back_populates='bill', uselist= False)

class Transaction(Base):
    __tablename__= 'transactions'

    id = Column(Integer, primary_key=True)
    bill_id= Column(Integer, ForeignKey('bills.id'), nullable= False)
    waiter_id= Column(Integer, ForeignKey('waiters.id'), nullable= False)
    tip_amount= Column(Integer, nullable= False)
    total_amount= Column(Integer, nullable= False)
    timestamp= Column(DateTime, default=datetime.utcnow)
    status= Column(String, default='failed')
    transaction_id= Column(String)
    is_settled = Column(Boolean, default=False)

    bill= relationship('Bill', back_populates='transaction', uselist=False)
    waiter= relationship('Waiter', back_populates='transactions')

class TipSettlement(Base):
    __tablename__='tip_settlements'

    id = Column(Integer, primary_key=True)
    waiter_id= Column(Integer, ForeignKey('waiters.id'), nullable=False)
    total_tips= Column(Integer, nullable=False)
    settled_at= Column(DateTime, default=datetime.utcnow)
    transaction_id= Column(String)

    waiter= relationship('Waiter', back_populates='tip_settlements')