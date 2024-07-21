from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey


request_appointment_association = db.Table(
    'request_appointments',
    db.Model.metadata,
    db.Column('request_id', db.Integer, db.ForeignKey('requests.id')),
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointments.id'))
)


months_users_association = db.Table(
    'months_users',
    db.Model.metadata,
    db.Column('month_id', db.Integer, db.ForeignKey('months.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)
