from app import db
from sqlalchemy import ForeignKey


class BaseAppointment(db.Model):
    __tablename__ = 'base_appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    center_id = db.Column(db.Integer, ForeignKey('centers.id'), nullable=False)
    week_day = db.Column(db.Text, nullable=False)
    week_index = db.Column(db.Integer, nullable=False)
    hour = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='base_appointments')
    center = db.relationship('Center', back_populates='base_appointments')
    