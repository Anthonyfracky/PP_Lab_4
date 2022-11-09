"""Init

Revision ID: ff8ac8d77bc1
Revises: 
Create Date: 2022-10-24 11:25:14.915525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff8ac8d77bc1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=120), nullable=False),
    sa.Column('first_name', sa.String(length=120), nullable=True),
    sa.Column('last_name', sa.String(length=120), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=150), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('info', sa.String(length=150), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wallet_id_2', sa.Integer(), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('amount_of_money', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=150), nullable=True),
    sa.Column('transaction_description', sa.String(length=150), nullable=True),
    sa.Column('wallet_id_1', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['wallet_id_1'], ['Wallets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Transactions')
    op.drop_table('Wallets')
    op.drop_table('users')
    # ### end Alembic commands ###
