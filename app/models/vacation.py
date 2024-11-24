import json
import math
import datetime
from app import db
from sqlalchemy import desc
import app.global_vars as global_vars
# from dateutil.relativedelta import relativedelta
from app.models import User, BaseAppointment, Month


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

        if start_date >= end_date:
            return "Data de início não pode ser posterior a data final", "danger"

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"

        if not user.pre_approved_vacation:
            flag = cls.check(start_date, user.id)

            if isinstance(flag, str):
                return flag

        flag = cls.check_past_vacations(start_date, end_date, user.id)
        if isinstance(flag, str):
            return flag       

        existing_vacation = cls.query.filter(
                            cls.user_id == user_id,
                            cls.status.in_(["pending_approval", "approved"])
                            ).all()
        
        if existing_vacation:
            return f"""Usuário tem férias pendentes.
                        Aguarde aprovação ou contacte o Administrador"""

        if end_date - start_date > datetime.timedelta(TOTAL_VACATION_DAYS):
            return f"Duração das férias ultrapassa o limite de {TOTAL_VACATION_DAYS} dias"

        new_vacation = cls(user_id=user_id,
                           start_date=start_date,
                           end_date=end_date,
                           status="pending_approval")

        db.session.add(new_vacation)
        db.session.commit()

        return new_vacation
    
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
        approved_vacations = cls.query.filter(cls.status.notin_(['denied', 'paid', 'completed'])).all()

        for vacation in approved_vacations:
            # if (vacation.start_date < datetime.date.today()) and vacation.status == 'pending_approval':
            #     vacation.status = 'denied'
            #     db.session.commit()
            if (vacation.end_date < datetime.date.today()) and vacation.status == 'ongoing':
                vacation.status = 'completed'
                db.session.commit()
            elif (vacation.start_date < datetime.date.today()) and vacation.status == 'approved':
                vacation.status = 'ongoing'
                db.session.commit()

            vacation_start = datetime.datetime.combine(vacation.start_date, datetime.datetime.min.time())
            flag = cls.check(vacation_start, vacation.user_id)
            if isinstance(flag, str):
                vacation.status = 'unapproved'
                db.session.commit()


                
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
    def check_concomitant_vacations(cls, start_date, end_date, user_id):
        pass


    @classmethod
    def check(cls, start_date, user_id):
        # user = User.query.filter_by(id=user_id).first()
        # vac_report = cls.get_vacation_report(start_date, user_id)

        # originals = vac_report.get('original')
        # realizeds = vac_report.get('realized')

        # if not originals or not realizeds:
        #     return "Erro ao buscar dados"
        
        # original_len = len([o for o in originals if o != -1])
        # if original_len < 3:
        #     return """Usuário não tem dados suficientes para solicitar férias.
        #             Por favor, façao o pedido diretamente ao Administrador"""

        # original_routine_avg = sum([o['routine'] for o in originals if o != -1])/original_len
        # original_plaintemps_avg = sum([o['plaintemps'] for o in originals if o != -1])/original_len

        # realized_len = len([r for r in realizeds if r != -1])
        # realized_routine_avg = sum([r['routine'] for r in realizeds])/realized_len
        # realized_plaintemps_avg = sum([r['plaintemps'] for r in realizeds])/realized_len

        # ora = math.ceil(original_routine_avg * 1.1)
        # opa = math.ceil(original_plaintemps_avg * 1.1)
        # rra = math.ceil(realized_routine_avg * 1.1)
        # rpa = math.ceil(realized_plaintemps_avg * 1.1)
        
        # rules = user.get_vacation_rules()

        # if rra < rules['routine'] or rpa < rules['plaintemps']:
        #     return "Usuário não manteve horas nas escalas realizadas para ter direito à férias" 

        # print(checked_all_months)
        return 0

    @classmethod
    def get_vacation_report(cls, start_date, user_id):
        return 0
        # user = User.query.filter_by(id=user_id).first()
        # if not user:
        #     return f"Usuário com id {user_id} não encontrado"

        # if not user.is_active:
        #     return "Usuário inativo. Não pode solicitar férias"

        # target_date = start_date.replace(year=start_date.year - 1)
        # if user.date_joined > target_date.date():
        #     return f"""Usuário entrou no grupo menos de um ano antes do
        #                 início das férias ({start_date.strftime('%d/%m/%Y')})"""
    
        # user_rules = user.get_vacation_rules()
        # base_dict = BaseAppointment.get_users_total(user.id, split_the_fifth=True)

        # if base_dict['routine'] < user_rules['routine'] or base_dict['plaintemps'] < user_rules['plaintemps']:
        #     return "Usuário não tem direito Base à férias"

        # str_month, str_year = int(start_date.strftime('%m')), int(start_date.strftime('%Y'))

        # months_num = []
        # for i in range(1, 13):
        #     months_num.append((str_month + i) % 12)
        
        # months_to_check = []
        # year = str_year
        # for i, month in enumerate(months_num):
        #     month = 12 if month == 0 else month
            
        #     if i == 0 and not month == 1:
        #         year -= 1

        #     if not year == str_year and month == 1:
        #         year = str_year
            
        #     months_to_check.append((month, year))

        # months_to_check = months_to_check[5:-1]

        # original_results = []
        # realized_results = []
        # for month, year in months_to_check:
        #     original_path = f"original_{month}_{year}.json"
        #     original_results.append(cls.check_original(original_path, user.crm, user_rules))
        #     realized_results.append(cls.check_realized(month, year, user.id))

        # return {"original": original_results, "realized": realized_results}
    
    @classmethod
    def check_realized(cls, month_num, month_year, user_id):  
        from app.global_vars import NIGHT_HOURS

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return 0

        appointments = [a for a in user.appointments if a.day.month.number == month_num]
        appointments = [a for a in appointments if a.day.month.year == month_year]

        realized_dict = {"routine": 0, "plaintemps": 0}
        for app in appointments:
            if app.day.is_holiday or app.hour in NIGHT_HOURS:
                realized_dict['plaintemps'] += 1
            else:
                realized_dict['routine'] += 1

        return realized_dict

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
            
            return orig_dict
                
        except FileNotFoundError:
            return -1

    @classmethod
    def report(cls):
        translation_dict = {
            "pending_approval": "Pendente",
            "approved": "Aprovado",
            "denied": "Negado",
            "completed": "Concluído",
            "ongoing": "Em andamento",
            "paid": "Pago",
            "unapproved": "Aprovação Retirada"
        }
        
        vacations = cls.query.order_by(desc(cls.id)).all()
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
        for i, month in enumerate(months):
            if not month:
                output += f"O mês {months_range[i][1]}/{months_range[i][0]} não foi encontrado\n"
                continue

            original_dict = month.get_original_dict()
            if not original_dict:
                output += f"O mês {months_range[i][1]}/{months_range[i][0]} não tem original\n"
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

    def pay(self):
        if self.status == "paid":
            return "Férias já pagas"
        
        if self.status == "pending_approval":
            return "Férias não podem ser pagas antes de aprovadas"

        if self.status == "denied":
            return "Férias negadas não podem ser pagas"

        self.status = "paid"
        db.session.commit()

        return 0

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