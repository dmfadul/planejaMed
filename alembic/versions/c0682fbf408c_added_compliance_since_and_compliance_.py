"""added compliance_since and compliance_history to User

Revision ID: c0682fbf408c
Revises: 9a1b20166467
Create Date: 2024-12-01 13:50:29.783375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0682fbf408c'
down_revision: Union[str, None] = '9a1b20166467'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('compliant_since', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('compliance_history', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'compliance_history')
    op.drop_column('users', 'compliant_since')
    # ### end Alembic commands ###
