from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey


request_appointment_association = db.Table(
    'request_appointments',
    db.Model.metadata,
    db.Column('request_id', db.Integer, db.ForeignKey('requests.id')),
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointments.id'))
)
