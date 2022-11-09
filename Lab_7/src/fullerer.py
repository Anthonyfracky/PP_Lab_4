import random

from faker import Faker
from src.db import session
from src.models import *

gen = Faker()


def create_user():
    for _ in range(10):
        user = User(
            username=gen.user_name(),
            first_name=gen.first_name(),
            last_name=gen.last_name(),
            email=gen.ascii_free_email(),
            password=gen.password(),
            phone=gen.phone_number(),
        )
        session.add(user)
    session.commit()


def create_wallet():
    users = session.query(User).all()
    for user in users:
        wallet = Wallet(
            balance=random.randint(500, 10000),
            currency=gen.sentence(),
            creation_date=gen.date(),
            info=gen.sentence(),
            user_id=user.id
        )
        session.add(wallet)
    session.commit()


def create_transaction():
    wallets = session.query(Wallet).all()
    for wallet in wallets:
        transaction = Transaction(
            wallet_id_2=random.randint(1, 10),
            date_time=gen.date(),
            amount_of_money=random.randint(10, 500),
            currency=gen.sentence(),
            transaction_description=gen.sentence(),
            wallet_id_1=wallet.id
        )
        session.add(transaction)
    session.commit()


if __name__ == '__main__':
    create_user()
    create_wallet()
    create_transaction()
