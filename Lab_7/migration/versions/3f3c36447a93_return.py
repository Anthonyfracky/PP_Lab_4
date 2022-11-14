"""return

Revision ID: 3f3c36447a93
Revises: f06e845db821
Create Date: 2022-11-11 00:44:49.526881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f3c36447a93'
down_revision = 'f06e845db821'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Transactions', 'wallet_id_2',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('Transactions_wallet_id_2_fkey', 'Transactions', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('Transactions_wallet_id_2_fkey', 'Transactions', 'Wallets', ['wallet_id_2'], ['id'], ondelete='CASCADE')
    op.alter_column('Transactions', 'wallet_id_2',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###