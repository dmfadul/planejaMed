from app import db, login_manager, bcrypt
from flask_login import UserMixin
from unidecode import unidecode
from sqlalchemy.orm import relationship
from datetime import datetime
from .associations import months_users_association


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

    is_visible = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)

    pre_approved_vacation = db.Column(db.Boolean, default=False)
    
    password = db.Column(db.Text, nullable=False)

    appointments = db.relationship('Appointment', back_populates='user', lazy=True)
    base_appointments = db.relationship('BaseAppointment', back_populates='user', lazy=True)

    requests_sent = db.relationship('Request', foreign_keys='Request.requester_id', back_populates='requester', lazy=True)
    requests_received = db.relationship('Request', foreign_keys='Request.responder_id', back_populates='responder', lazy=True)

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', lazy=True)
    logs = db.relationship('Log', back_populates='user', lazy=True)
    vacations = db.relationship('Vacation', back_populates='user', lazy=True)

    months = relationship(
        'Month',
        secondary=months_users_association,
        back_populates='users'
        )

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
    
    @classmethod
    def add_entry(cls, first_name, middle_name, last_name, crm, rqe, phone, email, password):
        from app.models import Message
        users = cls.query.all()
        names = [user.full_name for user in users]

        existing_user = cls.query.filter_by(crm=crm).first()
        
        if not existing_user:       
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

        elif existing_user.is_active:
            db.session.rollback()
            Message.new_message(sender_id=existing_user.id,
                                receivers_code="*",
                                content=f"""{existing_user.full_name}, usuário ativo,
                                está tentando criar uma nova conta com CRM já cadastrado""")
            
            return "CRM já cadastrado"
        elif existing_user.is_waiting_for_approval:
            db.session.rollback()
            return "Conta já existe. Aguarde a Liberação do Administrador"
        elif not existing_user.is_active:
            db.session.rollback()
            Message.new_message(sender_id=existing_user.id,
                    receivers_code="*",
                    content=f"""{existing_user.full_name}, ex-usuário,
                    está tentando criar uma nova conta""")
            return "Conta já existe, mas usuário não está ativo. Entre em contato com o Admin"
        elif new_user.full_name in names:
            db.session.rollback()
            return "Nome já cadastrado"
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
        return new_user
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

        return 0

    @classmethod
    def create_system_user(cls):
        system_user = cls(
            first_name='System',
            middle_name='',
            last_name='User',
            crm=0,
            rqe=0,
            phone='0',
            email='none@system.com',
            password='system'
        )
        db.session.add(system_user)
        db.session.commit()

        return system_user

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
    
    def get_month_appointments(self, month_num, year_num):
        appointments = [a for a in self.appointments if a.day.month.number == month_num]
        appointments = [a for a in appointments if a.day.month.year == year_num]
        apps = [(a.center.abbreviation, a.day.date.day, a.hour) for a in appointments if a.is_confirmed]

        return apps

    def get_month_requests(self, month_num, year_num):
        from app.models import Request

        reqs = Request.query.all()
        reqs = [req for req in reqs if req.action not in ['include_user', 'approve_vacation']]
        reqs = [req for req in reqs if self.full_name in req.info]
        reqs = [req for req in reqs if req.working_month == month_num]
        reqs = [req for req in reqs if req.working_year == year_num]
        reqs = [req for req in reqs if req.response == "authorized"]
        
        reqs_info = []
        for req in reqs:
            center = req.appointment_center
            day = req.appointment_date.day
            hour_range = req.appointment_hour_range

            if req.action == 'exchange':
                req_dict = {'INCLUDE' : (center, day, hour_range)}
                reqs_info.append((req.id, req_dict))
 
                center2 = req.appointment_center_two
                day2 = req.appointment_date_two.day
                hour_range2 = req.appointment_hour_range_two

                req_dict2 = {'EXCLUDE' : (center2, day2, hour_range2)}
                reqs_tuple = (req.id, req_dict2)
                if reqs_tuple not in reqs_info:
                    reqs_info.append(reqs_tuple)

                reqs_info.append((req.id, req_dict2))
            else:
                if req.action == 'donate' and req.signal(self.crm) == -1:
                    action = 'INCLUDE'
                elif req.action == 'donate' and req.signal(self.crm) == 1:
                    action = 'EXCLUDE'
                elif req.action == 'include_appointments':
                    action = 'EXCLUDE'
                elif req.action == 'exclude_appointments':
                    action = 'INCLUDE'           
                else:
                    action = 'UNKNOWN'
                
                req_dict = {action : (center, day, hour_range)}
                reqs_tuple = (req.id, req_dict)
                if reqs_tuple not in reqs_info:
                    reqs_info.append(reqs_tuple)

        reqs_info = sorted(reqs_info, key=lambda x: x[0], reverse=True)
        return reqs_info

    def get_original_appointments_by_month(self, month_num, year_num):
        month_apps = self.get_month_appointments(month_num, year_num)
        month_reqs = self.get_month_requests(month_num, year_num)

        # for app in month_apps:
        #     print(app)
        # for month_req in month_reqs:
        #     print(month_req)
        
        for month_req in month_reqs:
            req_dict = month_req[1]
            for action, req in req_dict.items():
                for hour in req[2]:
                    r = req[0], req[1], hour
                    if action == "EXCLUDE":
                        if not r in month_apps:
                            # print(1, action, month_req[0], r)
                            # continue
                            return "Erro: não foi possível gerar a lista de horários originais1"
                        
                        month_apps.remove(r)
    
                    elif action == "INCLUDE":
                        if r in month_apps:
                            # print(2, action, month_req[0], r)
                            # continue
                            return "Erro: não foi possível gerar a lista de horários originais2"
                        
                        month_apps.append(r)

        app_dict = {}
        for app in month_apps:
            center, day, hour = app
            
            if center not in app_dict:
                app_dict[center] = {}
            
            if str(day) not in app_dict[center]:
                app_dict[center][str(day)] = []
            
            app_dict[center][str(day)].append(hour)

        hours_order = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        order_map = {num: idx for idx, num in enumerate(hours_order)}

        for center in app_dict:
            for day in app_dict[center]:
                app_dict[center][day] = sorted(app_dict[center][day], key=lambda x: order_map[x])

        return app_dict

    @property
    def full_name(self):
        name = f'{self.first_name} {self.middle_name} {self.last_name}'
        return ' '.join(name.split())
    
    @property
    def abbreviated_name(self):
        non_abbr_words = {'de', 'da', 'do', 'dos', 'das', 'e', 'De', 'Da', 'Do', 'Dos', 'Das', 'E'}

        first_name_parts = self.first_name.split()
        middle_name_parts = self.middle_name.split()
        last_name_parts = self.last_name.split()

        abbr_name = first_name_parts[0] 

        for part in middle_name_parts:
            if part not in non_abbr_words:
                abbr_name += f" {part[0]}."

        if len(last_name_parts) == 1:
            abbr_name += f" {last_name_parts[0]}"
            return abbr_name
        
        for i, part in enumerate(last_name_parts):
            if part not in non_abbr_words:
                abbr_name += f" {part}"
                return abbr_name
            else:
                abbr_name += f" {part}"
                if len(last_name_parts[i+1]) > 5:
                    abbr_name += f" {last_name_parts[i+1][0]}."
                else:
                    abbr_name += f" {last_name_parts[i+1]}"
                    
                return abbr_name
    
    @property
    def app_dict(self):
        from app.models import Month

        current_month = Month.get_current()
        appointments = [app for app in self.appointments if app.day.month_id == current_month.id]
        appointments = [app for app in appointments if app.is_confirmed]

        app_dict = {}
        for app in appointments:
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

        schedule = []
        for center in self.app_dict:
            for date in self.app_dict[center]:
                appointments = split_hours(self.app_dict[center][date])
                for app in appointments:
                    hour = convert_hours_to_line(app)
                    schedule.append(f"{center} -- {date.strftime('%d/%m/%y')} -- {hour}")

        def sort_key(item):
            center, date_str, _ = item.split(" -- ")
            date = datetime.strptime(date_str, "%d/%m/%y")
            return (center, date)

        return ["INCLUSÃO"] + sorted(schedule, key=sort_key)
    
    @property
    def redundant_schedule(self):
        from app.hours_conversion import gen_redudant_hour_list
        schedule = []
        for center in self.app_dict:
            for date in self.app_dict[center]:

                appointments = gen_redudant_hour_list(self.app_dict[center][date], include_line=True)
                for app in appointments:
                    schedule.append(f"{center} -- {date.strftime('%d/%m/%y')} -- {app}")

        return sorted(schedule)
    
    @property
    def is_waiting_for_approval(self):
        open_requests = [req for req in self.requests_sent if req.is_open]
        if any([req.action == 'include_user' for req in open_requests]):
            return True

        return False

    def get_vacation_rules(self):
        from app.global_vars import VACATION_NEW_RULES, VACATION_OLD_RULES, VACATION_NEW_RULE_START

        if self.date_joined < VACATION_NEW_RULE_START.date():
            return VACATION_OLD_RULES

        return VACATION_NEW_RULES


    def hours(self, month_id):
        appointments = [app for app in self.appointments if app.day.month_id == month_id]

        hours_dict = {}
        for app in appointments:
            if app.center.abbreviation not in hours_dict:
                hours_dict[app.center.abbreviation] = [0, 0]
            
            if app.is_night or app.day.is_holiday:
                hours_dict[app.center.abbreviation][1] += 1
            else:
                hours_dict[app.center.abbreviation][0] += 1

        return hours_dict
            
    def base_row(self, center_id):
        from app.hours_conversion import convert_to_letter
        base_appointments = [app for app in self.base_appointments if app.center_id == center_id]
        
        app_dict = {}
        for app in base_appointments:
            key = (app.week_day, app.week_index)
            if key not in app_dict:
                app_dict[key] = [app.hour]
            else:
                app_dict[key].append(app.hour)

        for key in app_dict:
            app_dict[key] = convert_to_letter(app_dict[key])

        base_row = []
        for weekindex in list(range(1, 6)):
            for weekday in list(range(7)):
                if (weekday, weekindex) in app_dict:
                    base_row.append(app_dict[(weekday, weekindex)])
                else:
                    base_row.append('')

        return base_row
 
    def filtered_appointments(self, center_id, day_id, unified=False):
        from app.hours_conversion import convert_to_letter

        apps = [a.hour for a in self.appointments if a.is_confirmed and a.center_id == center_id and a.day_id == day_id]
        if not apps and not unified:
            return []
        if not apps and unified:
            return ''
        
        if unified:
            return convert_to_letter(apps)
        
        return apps

    def make_invisible(self):
        self.is_visible = False
        db.session.commit()
    
    def make_visible(self):
        self.is_visible = True
        db.session.commit()

    def make_admin(self):
        self.is_admin = True
        db.session.commit()
    
    def make_sudo(self):
        self.is_sudo = True
        db.session.commit()

    def make_root(self):
        self.is_root = True
        db.session.commit()

    def remove_privileges(self):
        self.is_admin = False
        self.is_sudo = False
        self.is_root = False
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

        self.password = hashed_password
        db.session.commit()

        return 0
    
    def gen_center_dict(self, month_id=None):
        from app.models import Month

        month_to_use = Month.get_current() if month_id is None else Month.query.filter_by(id=month_id).first()

        appointments = [app for app in self.appointments if app.day.month_id == month_to_use.id]
        appointments = [app for app in appointments if app.is_confirmed]

        app_dict = {}
        for app in appointments:
            center_abbr = app.center.abbreviation
            app_day = app.day.date.day
            
            if center_abbr not in app_dict:
                app_dict[center_abbr] = {}
            
            if app_day not in app_dict[center_abbr]:
                app_dict[center_abbr][app_day] = []
            
            app_dict[center_abbr][app_day].append(app.hour)

        return app_dict

    def has_vacations_rights(self):
        if not self.is_active or not self.is_visible:
            return False

        if self.pre_approved_vacation:
            return True
            