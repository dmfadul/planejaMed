import os
import json
from app import db
from app.models.log import Log
import app.global_vars as global_vars
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .associations import months_users_association


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
    users = relationship(
        'User',
        secondary=months_users_association,
        back_populates='months'
        )

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

    @classmethod
    def get_next(cls):
        current_month = cls.get_current()
        next_month = cls.query.filter_by(number=current_month.next_month[0],
                                         year=current_month.next_month[1]).first()
        return next_month
    
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
    def days_list(self):
        return [day.date.day for day in self.days]
    
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
    def appointments(self):
        return [appointment for day in self.days for appointment in day.appointments]
    
    def get_day(self, day_num):
        day_num = int(day_num)
        return [day for day in self.days if day.date.day == day_num][0]

    def populate(self):
        from app.models.day import Day
        from app.global_vars import SYSTEM_CRM

        if self.is_populated:
            return -1

        for date in self.dates_row:
            day = Day.add_entry(month_id=self.id, date=date)

            if day == -1:
                Log.new_log(
                    user_crm=SYSTEM_CRM,
                    action=f"Erro ao adicionar data {date} - Data {date} já existe."
                )
        
        
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
    
    def fix_users(self):
        from app.models import User
        active_users = User.query.filter_by(is_active=True, is_visible=True).all()
        effective_users = [appointment.user for day in self.days for appointment in day.appointments]

        self.users = list(set(active_users + effective_users))
        
        db.session.commit()
        return 0
    
    def add_user(self, user):
        self.users.append(user)
        db.session.commit()
        return 0
    
    def remove_user(self, user):
        for app in user.appointments:
            if app not in self.appointments:
                continue
            app.delete_entry()
            db.session.flush()

        if user in self.users:
            self.users.remove(user)

        db.session.commit()
        return 0
    
    def save_original(self):
        original_dict = {
            'number': self.number,
            'year': self.year,
            'leader': self.leader,
            'week_days': [global_vars.DIAS_SEMANA[d.weekday()][:3] for d in self.dates_row],
            'month_days': [d.day for d in self.dates_row],
            'holidays': [day.date.day for day in self.days if day.is_holiday],
            'data': {}
        }

        for doctor in sorted(self.users, key=lambda x: x.full_name):
            if not doctor.is_active or not doctor.is_visible:
                continue
            
            original_dict['data'][doctor.crm] = doctor.gen_center_dict(month_id=self.id)

        with open(f"instance/originals/original_{self.number}_{self.year}.json", 'w') as f:
            json.dump(original_dict, f, indent=2)

        return 0

    def get_original_dict(self):
        file_name = f"original_{self.number}_{self.year}.json"
       
        if file_name not in os.listdir('instance/originals'):
            return None
            
        with open(f"instance/originals/{file_name}", 'r') as f:
            original_dict = json.load(f)
        
        return original_dict

    def save_holiday_to_original(self, day, operation):
        original_dict = self.get_original_dict()
        
        if not original_dict:
            return -1

        holidays = original_dict.get('holidays')
        
        if operation == "add" and day not in holidays:
            holidays.append(day)
        elif operation == "remove":
            try:
                holidays.remove(day)
            except ValueError:
                print(f"Day {day} not found")
                return -1
        else:
            return -1

        original_dict['holidays'] = holidays

        with open(f"instance/originals/original_{self.number}_{self.year}.json", 'w') as f:
            json.dump(original_dict, f, indent=2)
        

    def get_users_realized_total(self, user_id):
        output = {"routine": 0, "plaintemps": 0}
        for app in [a for a in self.appointments if a.user_id == user_id]:
            if app.day.date.weekday() in [5, 6] or app.is_night:
                output["plaintemps"] += 1
            else:
                output["routine"] += 1

        return output
    
    def get_users_original_total(self, user_crm):
        from app.global_vars import NIGHT_HOURS 

        original_dict = self.get_original_dict()
        if not original_dict:
            return -1
        
        user_dict = original_dict['data'].get(str(user_crm))
        if not user_dict:
            return -2

        holidays = original_dict['holidays']
        if not holidays:
            return -3

        test1 = []
        test2 = []
        output = {"routine": 0, "plaintemps": 0}
        for center, data in user_dict.items():
            for day, apps in data.items():
                for app in apps:
                    if int(day) in holidays or app in NIGHT_HOURS:
                        test1.append((day, app))
                        output["plaintemps"] += 1
                    else:
                        test2.append((day, app))
                        output["routine"] += 1

        return output
