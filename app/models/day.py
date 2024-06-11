from app import db
from sqlalchemy import ForeignKey


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    month_id = db.Column(db.Integer, ForeignKey('months.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    is_holiday = db.Column(db.Boolean, default=False)

    month = db.relationship('Month', back_populates='days', lazy=True)
    appointments = db.relationship('Appointment', back_populates='day', lazy=True)

    def __repr__(self):
        return f"{self.date}"
    
    @classmethod
    def add_entry(cls, month_id, date):
        existing_dates = [day.date for day in cls.query.filter_by().all()]
        if date in existing_dates:
            return -1
        
        new_day = cls(
            month_id = month_id,
            date = date
        )
        
        db.session.add(new_day)
        db.session.commit()

        return new_day
    
    @property
    def key(self):
        weekindex = ((self.date - self.date.replace(day=1)).days // 7) + 1
        return self.date.weekday(), weekindex

    def add_holiday(self):
        self.is_holiday = True
        db.session.commit()
        return 0
    
    def remove_holiday(self):
        self.is_holiday = False
        db.session.commit()
        return 0
        