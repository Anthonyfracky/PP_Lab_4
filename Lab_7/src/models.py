from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime, Date

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120), nullable=False)
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)
    email = Column('email', String(100), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(100), nullable=True)
    wallets = relationship('Wallet', back_populates='user')


class Wallet(Base):
    __tablename__ = "Wallets"
    id = Column(Integer, primary_key=True)
    balance = Column(Integer)
    currency = Column(String(150), nullable=True)
    creation_date = Column(DateTime, default=datetime.now())
    info = Column(String(150))
    user_id = Column("user_id", ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='wallets')
    transactions = relationship('Transaction', back_populates='wallet')


class Transaction(Base):
    __tablename__ = "Transactions"
    id = Column(Integer, primary_key=True)
    wallet_id_1 = Column("wallet_id_1", ForeignKey('Wallets.id', ondelete='CASCADE'), nullable=False)
    wallet_id_2 = Column(Integer, nullable=True)
    amount_of_money = Column(Integer, nullable=True)
    currency = Column(String(150), nullable=True)
    date_time = Column(DateTime, default=datetime.now(), nullable=True)
    transaction_description = Column(String(150))
    wallet = relationship('Wallet', back_populates='transactions')
