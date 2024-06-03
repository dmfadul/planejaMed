from app import db
from sqlalchemy import ForeignKey
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requester_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    responder_id = db.Column(db.Integer, ForeignKey('users.id'))
    receivers = db.Column(db.Text, nullable=False)
    action = db.Column(db.Text, nullable=False)

    is_open = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())
    response_date = db.Column(db.Date, nullable=True)

    existing_appointment_id = db.Column(db.Integer, ForeignKey('appointments.id'), nullable=False)
    appointment_to_exchange_id = db.Column(db.Integer, ForeignKey('appointments.id'))
    doctor_who_will_cover_id = db.Column(db.Integer, ForeignKey('users.id'))
    doctor_to_include_id = db.Column(db.Integer, ForeignKey('users.id'))

    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='requests_sent', lazy=True)
    responder = db.relationship('User', foreign_keys=[responder_id], back_populates='requests_received', lazy=True)
    existing_appointment = db.relationship('Appointment', foreign_keys=[existing_appointment_id], back_populates='general_requests', lazy=True)
    appointment_to_exchange = db.relationship('Appointment', foreign_keys=[appointment_to_exchange_id], back_populates='requests_to_exchange', lazy=True)
    doctor_who_will_cover = db.relationship('User', foreign_keys=[doctor_who_will_cover_id], lazy=True)
    doctor_to_include = db.relationship('User', foreign_keys=[doctor_to_include_id], lazy=True)
    
    def __repr__(self):
        return f'{self.requester} - {self.action} - {self.is_open}'
    