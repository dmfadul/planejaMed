from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey


month_day_association = Table('month_day', db.Model.metadata,
    Column('day_id', Integer, ForeignKey('days.id'), primary_key=True),
    Column('month_id', Integer, ForeignKey('months.id'), primary_key=True)
)
