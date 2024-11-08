from app import db
from app.models import User, BaseAppointment, Month
import app.global_vars as global_vars
from dateutil.relativedelta import relativedelta
import datetime
import json


class Vacation(db.Model):
    __tablename__ = "vacations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False, default='pending_approval')

    user = db.relationship('User', back_populates='vacations', lazy=True)

    @property
    def year(self):
        return self.start_date.year

    @classmethod
    def add_entry(cls, user_id, start_date, end_date):
        from app.global_vars import TOTAL_VACATION_DAYS

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"

        check = cls.query.filter(
            cls.user_id == user_id,
            cls.status.in_(["pending_approval", "approved"])
        ).all()
        
        if check:
            return f"""Usuário tem férias pendentes.
                        Aguarde aprovação ou contacte o Administrador"""

        if end_date - start_date > datetime.timedelta(TOTAL_VACATION_DAYS):
            return f"Duração das férias ultrapassa o limite de {TOTAL_VACATION_DAYS} dias"

        vacation = cls(user_id=user_id,
                       start_date=start_date,
                       end_date=end_date,
                       status="pending_approval")

        db.session.add(vacation)
        db.session.commit()

        return vacation
    
    def remove_entry(self):
        db.session.delete(self)
        db.session.commit()
        return 0

    def approve(self):
        self.status = "approved"
        db.session.commit()
        return 0

    def deny(self):
        self.status = "denied"
        db.session.commit()
        return 0

    @classmethod
    def update_status(cls):
        approved_vacations = cls.query.filter_by(status='approved').all()
        for vacation in approved_vacations:
            if vacation.end_date < datetime.date.today():
                vacation.status = 'completed'
                db.session.commit()
                return 0

            if vacation.start_date < datetime.date.today():
                vacation.status = 'ongoing'
                db.session.commit()
                return 0
                
    @classmethod
    def check_past_vacations(cls, start_date, end_date, user_id):
        from app.global_vars import MAX_VACATION_SPLIT, MIN_VACATION_DURATION, TOTAL_VACATION_DAYS

        vacations = cls.query.filter_by(user_id=user_id).filter(~cls.status.in_(['pending_approval', 'denied', 'cancelled'])).all()
        vacations = [vacation for vacation in vacations if vacation.year == start_date.year]
        
        if len(vacations) == 0:
            return 0

        if len(vacations) == MAX_VACATION_SPLIT:
            return "Usuário já utilizou todas as férias este ano este ano"
        
        old_vacation = vacations[0]
        old_vac_duration = old_vacation.end_date - old_vacation.start_date
        new_vac_duration = end_date - start_date

        if old_vac_duration.days > TOTAL_VACATION_DAYS - MIN_VACATION_DURATION:
            return "Usuário já utilizou todas as férias este ano este ano"

        if old_vac_duration.days < MIN_VACATION_DURATION:
            old_vac_duration = datetime.timedelta(MIN_VACATION_DURATION)

        if old_vac_duration.days + new_vac_duration.days > TOTAL_VACATION_DAYS:
            return "O total de férias ultrapassa o limite"
    
        return 0

    @classmethod
    def check(cls, start_date, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"

        if not user.is_active:
            return "Usuário inativo. Não pode solicitar férias"

        target_date = start_date.replace(year=start_date.year - 1)
        if user.date_joined > target_date.date():
            return f"""Usuário entrou no grupo menos de um ano antes do
                        início das férias ({start_date.strftime('%d/%m/%Y')})"""
    
        user_rules = user.get_vacation_rules()
        base_dict = BaseAppointment.get_users_total(user.id, split_the_fifth=True)

        if base_dict['routine'] < user_rules['routine'] or base_dict['plaintemps'] < user_rules['plaintemps']:
            return "Usuário não tem direito Base à férias"

        str_month, str_year = int(start_date.strftime('%m')), int(start_date.strftime('%Y'))

        months_num = []
        for i in range(1, 13):
            months_num.append((str_month + i) % 12)
        
        months_to_check = []
        year = str_year
        for i, month in enumerate(months_num):
            month = 12 if month == 0 else month
            
            if i == 0 and not month == 1:
                year -= 1

            if not year == str_year and month == 1:
                year = str_year
            
            months_to_check.append((month, year))

        original_results = []
        realized_results = []
        for month, year in months_to_check:
            original_path = f"original_{month}_{year}.json"
            original_results.append(cls.check_original(original_path, user.crm, user_rules))
            realized_results.append(cls.check_realized(month, year, user.id))

        if any([result == 0 for result in original_results]) or any([result == 0 for result in realized_results]):
            return "Usuário não tem horas suficientes no original ou realizado"

        return 0
    
    @classmethod
    def check_realized(cls, month_num, month_year, user_id):
        month = Month.query.filter_by(number=month_num, year=month_year).first()
        if not month:
            return -1
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return -2
        
        user_rules = user.get_vacation_rules()
        month_dict = month.get_users_total(user_id)

        if month_dict['routine'] > user_rules['routine'] and month_dict['plaintemps'] > user_rules['plaintemps']:
            return 1

        if month_dict['routine'] + 12 > user_rules['routine'] and month_dict['plaintemps'] + 12 > user_rules['plaintemps']:
            return 2
        
        if month_dict['routine'] + 24 > user_rules['routine'] and month_dict['plaintemps'] + 24 > user_rules['plaintemps']:
            return 3

        return 0

    @classmethod
    def check_original(cls, original_path, user_crm, user_rules):
        from app.global_vars import NIGHT_HOURS

        try:
            with open(f"instance/originals/{original_path}", 'r') as file:
                original_file = json.load(file)
            
            data = original_file.get('data')
            holidays = original_file.get('holidays')
            doctor_dict = data.get(str(user_crm))
                
            orig_dict = {"routine": 0, "plaintemps": 0}
            for center, days_dict in doctor_dict.items():
                for day, hours in days_dict.items():
                    for hour in hours:
                        if int(day) in holidays or hour in NIGHT_HOURS:
                            orig_dict['plaintemps'] += 1
                        else:
                            orig_dict['routine'] += 1

            if orig_dict['routine'] < user_rules['routine'] or orig_dict['plaintemps'] < user_rules['plaintemps']:
                return 0
            
            return 1
                
        except FileNotFoundError:
            return -1

    @classmethod
    def report(cls):
        translation_dict = {
            "pending_approval": "Pendente",
            "approved": "Aprovado",
            "denied": "Negado",
            "completed": "Concluído",
            "ongoing": "Em andamento"
        }
        
        vacations = cls.query.all()
        output = []
        for vacation in vacations:
            output.append({
                "id": vacation.id,
                "name": vacation.user.full_name,
                "crm": vacation.user.crm,
                "start_date": vacation.start_date.strftime('%d/%m/%Y'),
                "end_date": vacation.end_date.strftime('%d/%m/%Y'),
                "status": translation_dict.get(vacation.status)
        })
        
        return output

    def calculate_payment(self):
        from app.hours_conversion import convert_hours_to_line, sum_hours
        months_range = self.get_months_range()
        months = self.get_months_in_range(months_range)
        
        output = ""
        for month in months:       
            original_dict = month.get_original_dict()
            if not original_dict:
                output += f"O mês {self.number}/{self.year} não tem original registrado\n"
                continue
            
            doctors_dict = original_dict.get('data').get(str(self.user.crm))

            if not doctors_dict:
                output += f"O médico {self.doctor.full_name} não tem horas no original do mês {month[1]}/{month[0]}\n"
                continue

            output_lst = []
            for center, value in doctors_dict.items():
                for day_str, hours in value.items():
                    day = month.get_day(day_str)
                    if not self.start_date <= day.date <= self.end_date:
                        continue

                    weekday = global_vars.DIAS_SEMANA[day.date.weekday()]
                    output_lst.append((day, weekday, hours, center))

            output_lst = sorted(output_lst, key=lambda x: x[0].date)

            total_p, total_r = 0, 0
            for d, wday, hrs, c in output_lst:
                hours_dict = sum_hours(hrs, wday)
                total_p += hours_dict['plaintemps']
                total_r += hours_dict['routine']

                date_str = d.date.strftime('%d/%m')
                hours = convert_hours_to_line(hrs)

                output += f"Dia {date_str} - {wday} - {hours} - {c}\n"

            output += "\n"
            output += f"Total de plantões: {total_p} horas - Total de rotinas: {total_r} horas \n"

        return output

    def get_months_range(self):
        curr_year, curr_month = self.start_date.year, self.start_date.month

        months = []
        while (curr_year, curr_month) <= (self.end_date.year, self.end_date.month):
            months.append((curr_year, curr_month))

            curr_month += 1
            if curr_month > 12:
                curr_month = 1
                curr_year += 1
        
        if global_vars.STR_DAY <= self.start_date.day <= 31:
            months.pop(0)

        if global_vars.STR_DAY <= self.end_date.day <= 31:
            extra_month = self.end_date.month + 1
            if extra_month == 13:
                extra_month = 1
                extra_year = self.end_date.year + 1
            else:
                extra_year = self.end_date.year
            months.append((extra_year, extra_month))

        return months

    def get_months_in_range(self, months_range):
        months_obj = []
        for year_month in months_range:
            month = Month.query.filter_by(number=year_month[1], year=year_month[0]).first()
            months_obj.append(month)

        return months_obj