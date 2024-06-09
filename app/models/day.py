from app import db
from sqlalchemy import ForeignKey


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    month_id = db.Column(db.Integer, ForeignKey('months.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    is_holiday = db.Column(db.Boolean, default=False)

    appointments = db.relationship('Appointment', back_populates='day', lazy=True)
    month = db.relationship('Month', back_populates='days', lazy=True)

    def __repr__(self):
        return self.date
    