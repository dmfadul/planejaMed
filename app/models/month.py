from app import db
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta
import app.global_vars as global_vars


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    leader = db.Column(db.String(100))
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
    def create_new_month(cls, number, year, leader=None):
        leader = leader or global_vars.LEADER
        existing_months = cls.query.filter_by(number=number, year=year).all()
        if existing_months:
            return -1
        
        month = cls(number=number, year=year, leader=leader)
        month.is_locked = True

        db.session.add(month)
        db.session.commit()
        return month
    
    @classmethod
    def delete(cls, number, year):
        month_to_delete = cls.query.filter_by(number=number, year=year).first()
        if month_to_delete.is_current:
            prv_month, prv_year = month_to_delete.previous_month
            new_current = cls.query.filter_by(number=prv_month, year=prv_year).first()
            new_current.set_current()

        month_to_delete.depopulate()
        
        db.session.delete(month_to_delete)
        db.session.commit()
        return 0
        
    @classmethod
    def get_current(cls):
        return cls.query.filter_by(is_current=True).first()

    @property
    def is_latest(self):
        return self == Month.query.order_by(Month.year.desc(), Month.number.desc()).first()

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
    def first_day(self):
        return sorted(self.days, key=lambda x: x.date)[0]
    
    @property
    def last_day(self):
        return sorted(self.days, key=lambda x: x.date)[-1]
    
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
    def calendar(self):
        month = []
        week = [""] * 7
        current_date = self.first_day.date

        while current_date <= self.last_day.date:
            week[current_date.weekday()] = current_date.day
            if current_date.weekday() == 6:
                month.append(week)
                week = [""] * 7
            current_date += timedelta(days=1)

        if week != [""] * 7:
            month.append(week)
            
        return month
    
    @property
    def holidays(self):
        return [day.date.day for day in self.days if day.is_holiday]
    
    @property
    def users(self):
        users = list(set([appointment.user for day in self.days for appointment in day.appointments]))
        return sorted(users, key=lambda x: x.full_name)
    
    @property
    def appointments(self):
        return [appointment for day in self.days for appointment in day.appointments]
    
    def get_day(self, day_num):
        return [day for day in self.days if day.date.day == day_num][0]

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
            day.delete()
        self.is_populated = False
        db.session.commit()
        return 0
    
    def gen_appointments(self):
        from app.models.appointment import Appointment
        from app.models.base import BaseAppointment
        from sqlalchemy.orm import joinedload

        if not self.is_populated:
            return -1
        
        base_appointments = BaseAppointment.query.options(
            joinedload(BaseAppointment.user),
            joinedload(BaseAppointment.center)
        ).filter(
            BaseAppointment.week_day.in_([day.key[0] for day in self.days]),
            BaseAppointment.week_index.in_([day.key[1] for day in self.days])
        ).all()

        # Create a mapping for day keys to day objects for quick lookup
        day_map = {(day.key[0], day.key[1]): day for day in self.days}

        base_app_map = {}         
        for b_app in base_appointments:
            if (b_app.week_day, b_app.week_index) not in base_app_map:
                base_app_map[(b_app.week_day, b_app.week_index)] = []
            base_app_map[(b_app.week_day, b_app.week_index)].append(b_app)

        appointments = []
        for day in self.days:
            day_base_apps = base_app_map.get(day.key)
            if not day_base_apps:
                continue

            for b_app in day_base_apps:
                print(b_app.user.full_name, b_app.center.abbreviation, day.date, b_app.hour)
                appointments.append(Appointment(user_id=b_app.user_id,
                                                center_id=b_app.center_id,
                                                day_id=day.id,
                                                hour=b_app.hour))

        if appointments:
            Appointment.add_entries(appointments)
        
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