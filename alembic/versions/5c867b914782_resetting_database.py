"""resetting database

Revision ID: 5c867b914782
Revises: 712e9d4e8ab1
Create Date: 2024-07-27 15:18:56.443636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c867b914782'
down_revision: Union[str, None] = '712e9d4e8ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('centers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('abbreviation', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('months',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('leader', sa.String(length=100), nullable=True),
    sa.Column('is_populated', sa.Boolean(), nullable=True),
    sa.Column('is_locked', sa.Boolean(), nullable=True),
    sa.Column('is_current', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number', 'year', name='uq_month_year')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('middle_name', sa.Text(), nullable=True),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.Column('crm', sa.Integer(), nullable=False),
    sa.Column('rqe', sa.Integer(), nullable=False),
    sa.Column('phone', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('date_joined', sa.Date(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_sudo', sa.Boolean(), nullable=True),
    sa.Column('is_root', sa.Boolean(), nullable=True),
    sa.Column('is_visible', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('crm')
    )
    op.create_table('base_appointments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('center_id', sa.Integer(), nullable=False),
    sa.Column('week_day', sa.Integer(), nullable=False),
    sa.Column('week_index', sa.Integer(), nullable=False),
    sa.Column('hour', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['center_id'], ['centers.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('days',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('month_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('is_holiday', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['month_id'], ['months.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('creation_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('months_users',
    sa.Column('month_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['month_id'], ['months.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table('requests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('requester_id', sa.Integer(), nullable=False),
    sa.Column('responder_id', sa.Integer(), nullable=True),
    sa.Column('receivers_code', sa.Text(), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('creation_date', sa.Date(), nullable=False),
    sa.Column('is_open', sa.Boolean(), nullable=True),
    sa.Column('response_date', sa.Date(), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('info', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['responder_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('center_id', sa.Integer(), nullable=False),
    sa.Column('day_id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.Column('hour', sa.Integer(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=True),
    sa.CheckConstraint('hour >= 0 AND hour < 24', name='valid_hour_range'),
    sa.ForeignKeyConstraint(['center_id'], ['centers.id'], ),
    sa.ForeignKeyConstraint(['day_id'], ['days.id'], ),
    sa.ForeignKeyConstraint(['request_id'], ['requests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.Column('receivers_code', sa.Text(), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('creation_date', sa.Date(), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['requests.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
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
    op.drop_table('messages')
    op.drop_table('appointments')
    op.drop_table('requests')
    op.drop_table('months_users')
    op.drop_table('logs')
    op.drop_table('days')
    op.drop_table('base_appointments')
    op.drop_table('users')
    op.drop_table('months')
    op.drop_table('centers')
    # ### end Alembic commands ###
