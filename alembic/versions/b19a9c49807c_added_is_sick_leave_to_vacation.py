"""added is_sick_leave to Vacation

Revision ID: b19a9c49807c
Revises: 5b52e38d0b5f
Create Date: 2024-12-03 17:46:27.848934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b19a9c49807c'
down_revision: Union[str, None] = '5b52e38d0b5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vacations', sa.Column('is_sick_leave', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vacations', 'is_sick_leave')
    # ### end Alembic commands ###