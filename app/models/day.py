from app import db
from sqlalchemy import ForeignKey
from .associations import month_day_association


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    is_holiday = db.Column(db.Boolean, default=False)

    months = db.relationship('Month', secondary=month_day_association, back_populates='days', lazy=True)
    appointments = db.relationship('Appointment', back_populates='day', lazy=True)

    def __repr__(self):
        return self.date
    

    @classmethod
    def add_entry(cls, month_id, date):
        existing_dates = [day.date for day in Day.query.filter_by().all()]
        if date in existing_dates:
            return -1
        
        new_day = cls(
            month_id = month_id,
            date = date
        )

        db.session.add(new_day)
        db.session.commit()

        return new_day
    