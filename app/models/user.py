from app import db, login_manager, bcrypt
from flask_login import UserMixin
from unidecode import unidecode
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    first_name = db.Column(db.Text, nullable=False)
    middle_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=False)

    crm = db.Column(db.Integer, nullable=False, unique=True)
    rqe = db.Column(db.Integer, nullable=False, unique=False)

    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    date_joined = db.Column(db.Date, default=datetime.now())
    is_admin = db.Column(db.Boolean, default=False)
    is_sudo = db.Column(db.Boolean, default=False)
    is_root = db.Column(db.Boolean, default=False)

    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=True)
    
    password = db.Column(db.Text, nullable=False)

    appointments = db.relationship('Appointment', back_populates='user', lazy=True)
    base_appointments = db.relationship('BaseAppointment', back_populates='user', lazy=True)

    requests_sent = db.relationship('Request', foreign_keys='Request.requester_id', back_populates='requester', lazy=True)
    requests_received = db.relationship('Request', foreign_keys='Request.responder_id', back_populates='responder', lazy=True)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
    
    @classmethod
    def add_entry(cls, first_name, middle_name, last_name, crm, rqe, phone, email, password):
        users = cls.query.all()
        crms = [user.crm for user in users]
        names = [user.full_name for user in users]
        
        new_user = cls(
            first_name = first_name,
            middle_name = middle_name,
            last_name = last_name,
            crm = crm,
            rqe = rqe,
            phone = phone,
            email = email,
            password = password
        )

        db.session.add(new_user)
        if int(new_user.crm) in crms:
            db.session.rollback()
            return -1
        if new_user.full_name in names:
            db.session.rollback()
            return -2
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return new_user

    @classmethod
    def get_by_name(cls, full_name):
        full_name_clean = unidecode(' '.join([part.strip().lower() for part in full_name.split()]))
        users = cls.query.all()
        names = [unidecode(user.full_name.lower()) for user in users]

        if names.count(full_name_clean) == 0:
            return -1
        
        if names.count(full_name_clean) == 1:
            for user in users:
                if unidecode(user.full_name.lower()) == full_name_clean:
                    return user
                
        return -2
    
    @property
    def full_name(self):
        name = f'{self.first_name} {self.middle_name} {self.last_name}'
        return ' '.join(name.split())
    
    @property
    def abbreviated_name(self):
        name = f'{self.first_name} {self.last_name}'
        return ' '.join(name.split())
    
    @property
    def app_dict(self):
        app_dict = {}
        for app in self.appointments:
            center_abbr = app.center.abbreviation
            app_date = app.day.date
            
            if center_abbr not in app_dict:
                app_dict[center_abbr] = {}
            
            if app_date not in app_dict[center_abbr]:
                app_dict[center_abbr][app_date] = []
            
            app_dict[center_abbr][app_date].append(app.hour)

        return app_dict
    
    @property
    def schedule(self):
        from app.hours_conversion import split_hours, convert_hours_to_line       
        schedule = ["-"]
        for center in self.app_dict:
            for date in self.app_dict[center]:
                appointments = split_hours(self.app_dict[center][date])
                for app in appointments:
                    hour = convert_hours_to_line(app)
                    schedule.append(f"{center} -- {date.strftime('%d/%m/%y')} -- {hour}")

        return sorted(schedule)
    
    def hours(self, month_id):
        appointments = [app for app in self.appointments if app.day.month_id == month_id]

        hours_dict = {}
        for app in appointments:
            if app.center.abbreviation not in hours_dict:
                hours_dict[app.center.abbreviation] = [0, 0]
            
            if app.is_night or app.day.is_holiday:
                hours_dict[app.center.abbreviation][1] += 1

            hours_dict[app.center.abbreviation][0] += 1

        print(hours_dict)
        return hours_dict
            


    def base_row(self, center_id):
        from app.hours_conversion import unify_appointments
        base_appointments = [app for app in self.base_appointments if app.center_id == center_id]
        
        app_dict = {}
        for app in base_appointments:
            key = (app.week_day, app.week_index)
            if key not in app_dict:
                app_dict[key] = [app.hour]
            else:
                app_dict[key].append(app.hour)

        for key in app_dict:
            app_dict[key] = unify_appointments(app_dict[key])

        base_row = []
        for weekindex in list(range(1, 6)):
            for weekday in list(range(7)):
                if (weekday, weekindex) in app_dict:
                    base_row.append(app_dict[(weekday, weekindex)])
                else:
                    base_row.append('')

        return base_row
 
    def filtered_appointments(self, center_id, day_id, unified=False):
        from app.hours_conversion import unify_appointments

        apps = [a.hour for a in self.appointments if a.center_id == center_id and a.day_id == day_id]
        if not apps and not unified:
            return []
        if not apps and unified:
            return ''
        
        if unified:
            return unify_appointments(apps)
        
        return apps

    def lock(self):
        self.is_locked = True
        db.session.commit()
    
    def unlock(self):
        self.is_locked = False
        db.session.commit()
    
    def activate(self):
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        self.is_active = False
        db.session.commit()

    def edit(self,
             first_name=None,
             middle_name=None,
             last_name=None,
             crm=None,
             rqe=None,
             phone=None,
             email=None):
        if first_name is not None:
            self.first_name = first_name
        if middle_name is not None:
            self.middle_name = middle_name
        if last_name is not None:
            self.last_name = last_name
        if crm is not None:
            self.crm = crm
        if rqe is not None:
            self.rqe = rqe
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email

        try:
            db.session.commit()
            return 0
        except Exception as e:
            db.session.rollback()
            return e

    def set_password(self, new_password):
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # self.password = hashed_password
        self.password = new_password
        db.session.commit()

        return 0
    