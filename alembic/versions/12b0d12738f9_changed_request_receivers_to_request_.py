"""changed Request.receivers to Request.receivers_code again

Revision ID: 12b0d12738f9
Revises: 46905bb5d9cf
Create Date: 2024-06-16 18:40:56.042179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '12b0d12738f9'
down_revision: Union[str, None] = '46905bb5d9cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('receivers_code', sa.Text(), nullable=False))
    op.drop_column('requests', 'receivers')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('receivers', mysql.TEXT(), nullable=False))
    op.drop_column('requests', 'receivers_code')
    # ### end Alembic commands ###
