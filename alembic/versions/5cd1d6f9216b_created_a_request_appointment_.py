"""created a request_appointment_association

Revision ID: 5cd1d6f9216b
Revises: b4abacb2efef
Create Date: 2024-07-08 20:55:25.003917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cd1d6f9216b'
down_revision: Union[str, None] = 'b4abacb2efef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request_appointments',
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.Column('appointment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['request_id'], ['requests.id'], )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('request_appointments')
    # ### end Alembic commands ###
