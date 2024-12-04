"""added is_checked to Month

Revision ID: 5b52e38d0b5f
Revises: c0682fbf408c
Create Date: 2024-12-01 15:44:31.168173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b52e38d0b5f'
down_revision: Union[str, None] = 'c0682fbf408c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('months', sa.Column('is_checked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('months', 'is_checked')
    # ### end Alembic commands ###