from app import db
from sqlalchemy import ForeignKey


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # user_crm = db.Column(db.Integer, ForeignKey('users.crm'), nullable=False)
    center = db.Column(db.Text, nullable=False)
    year = db.Column(db.Text, nullable=False)
    month = db.Column(db.Text, nullable=False)
    month_day = db.Column(db.Integer, nullable=False)
    week_day = db.Column(db.Text, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    is_holiday = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)