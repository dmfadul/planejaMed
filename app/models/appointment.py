from app import db
from sqlalchemy import ForeignKey


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # user_crm = db.Column(db.Integer, ForeignKey('users.crm'), nullable=False)
    center = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    month_id = db.Column(db.Integer, ForeignKey('months.id'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    is_locked = db.Column(db.Boolean, default=False)