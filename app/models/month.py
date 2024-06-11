from app import db
from sqlalchemy import ForeignKey, UniqueConstraint
from datetime import datetime, timedelta
import instance.global_vars as global_vars


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_populated = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    is_current = db.Column(db.Boolean, default=False)

    days = db.relationship('Day', back_populates='month', lazy=True)

    __table_args__ = (
        UniqueConstraint('number', 'year', name='uq_month_year'),
    )

    def __repr__(self):
        return f"{self.number}/{self.year}"  

    @classmethod
    def create_new_month(cls, number, year):
        existing_months = cls.query.filter_by(number=number, year=year).all()
        if existing_months:
            return -1
        
        month = cls(number=number, year=year)
        month.is_locked = True

        db.session.add(month)
        db.session.commit()
        return month
        
    @classmethod
    def get_current(cls):
        return cls.query.filter_by(is_current=True).first()

    @property
    def name(self):
        return global_vars.MESES[self.number-1]
    
    @property
    def previous_month(self):
        if self.number == 1:
            return 12, self.year - 1
        return self.number - 1, self.year

    @property
    def next_month(self):
        if self.number == 12:
            return 1, self.year + 1
        return self.number + 1, self.year
    
    @property
    def next_month_name(self):
        if self.number == 12:
            return global_vars.MESES[0]
        return global_vars.MESES[self.number]

    @property
    def dates_row(self):
        start_date = datetime(self.previous_month[1], self.previous_month[0], global_vars.STR_DAY)
        end_date = datetime(self.year, self.number, global_vars.STR_DAY-1)

        dates_row = []
        while start_date <= end_date:
            dates_row.append(start_date)
            start_date += timedelta(days=1)
        
        return dates_row
    
    @property
    def holidays(self):
        return [day for day in self.days if day.is_holiday]
    
    def populate(self):
        from app.models.day import Day

        if self.is_populated:
            return -1

        for date in self.dates_row:
            day = Day.add_entry(month_id=self.id, date=date)

            if day == -1:
                print(f"Data {date} já existe.")
        
            if date.weekday() in [5, 6]:
                day.is_holiday = True
                db.session.commit()

        self.is_populated = True
        db.session.commit()
        return 0
    
    def depopulate(self):
        for day in self.days[:]:
            self.days.remove(day)
        self.is_populated = False
        db.session.commit()
        return 0
    
    def gen_appointments(self):
        from app.models.appointment import Appointment
        from app.models.base import BaseAppointment

        if not self.is_populated:
            return -1

        for day in self.days:
            base_appointments = BaseAppointment.query.filter_by(
                                                                week_day=day.key[0],
                                                                week_index=day.key[1]
                                                                ).all()
            
            for b_app in base_appointments:
                print(b_app.user.full_name, b_app.center.abbreviation, day.date, b_app.hour)
                Appointment.add_entry(user_id=b_app.user_id,
                                      center_id=b_app.center_id,
                                      day_id=day.id,
                                      hour=b_app.hour)
        return 0

    def lock(self):
        self.is_locked = True
        db.session.commit()
        return 0
    
    def unlock(self):
        self.is_locked = False
        db.session.commit()
        return 0

    def set_current(self):
        if self.is_current:
            return -1
        
        existing_current = Month.query.filter_by(is_current=True).first()
        if existing_current:
            existing_current.is_current = False
            db.session.commit()      

        self.is_current = True
        db.session.commit()

        return 0