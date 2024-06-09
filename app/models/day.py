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
        return f"{self.date}"
    
    @classmethod
    def add_entry(cls, date, month_ids=None):
        from app.models import Month
        month_ids = month_ids or []

        existing_dates = [day.date for day in Day.query.filter_by().all()]
        if date in existing_dates:
            return -1
        
        new_day = cls(
            date = date
        )
        
        for month_id in month_ids:
            month = Month.query.get(month_id)
            if month:
                new_day.months.append(month)

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
    
    def add_to_month(self, month_id):
        from app.models import Month

        month = Month.query.get(month_id)
        if month and month not in self.months:
            self.months.append(month)
            db.session.commit()
            return self
        return 1
    