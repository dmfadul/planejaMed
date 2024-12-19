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
    is_sick_leave = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='vacations', lazy=True)

    @property
    def year(self):
        return self.start_date.year


#================================== HELPER METHODS ==================================#
    @classmethod
    def add_entry(cls, user_id, start_date, end_date, is_sick_leave=False):
        from app.global_vars import TOTAL_VACATION_DAYS

        if start_date >= end_date:
            return "Data de início não pode ser posterior a data final"

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"  

        new_vacation = cls(user_id=user_id,
                           start_date=start_date,
                           end_date=end_date,
                           is_sick_leave=is_sick_leave,
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

    def delete(self):
        self.status = "deleted"
        db.session.commit()
        return 0
    
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

    @classmethod
    def update_status(cls):
        shifting_vacations = cls.query.filter(cls.status.in_(['pending_approval',
                                                              'approved',
                                                              'ongoing'])).all()

        for vacation in shifting_vacations:
            if (vacation.status == 'pending_approval') and (vacation.start_date < datetime.date.today()):
                vacation.status = 'denied'
                db.session.commit()
            if (vacation.status in ['ongoing', 'approved']) and (vacation.end_date < datetime.date.today()):
                vacation.status = 'completed'
                db.session.commit()
            elif (vacation.status == 'approved') and (vacation.start_date < datetime.date.today()):
                vacation.status = 'ongoing'
                db.session.commit()


#=============================== QUERY METHODS ================================================#    
    @classmethod
    def check_vacations_availability(cls, start_date, end_date, user_id):
        """Check if user has used all vacation days or if the total requested days exceed the limit"""

        from app.global_vars import MAX_VACATION_SPLIT, MIN_VACATION_DURATION, TOTAL_VACATION_DAYS, SICK_LEAVE_TO_VACATION

        vacations = cls.query.filter_by(user_id=user_id).filter(cls.status.in_(['defered',
                                                                                'approved',
                                                                                'ongoing',
                                                                                'completed',
                                                                                'paid'])).all()
        vacations = [vacation for vacation in vacations if vacation.year == start_date.year]
        
        if len(vacations) == 0:
            return 0

        if len(vacations) >= MAX_VACATION_SPLIT:
            return "Usuário já utilizou todas as férias este ano este ano"
        
        old_vacation = vacations[0]
        old_vac_duration = old_vacation.end_date - old_vacation.start_date
        if old_vacation.is_sick_leave and old_vac_duration.days > 3:
            old_vac_duration = datetime.timedelta(SICK_LEAVE_TO_VACATION)
        new_vac_duration = end_date - start_date

        max_remainder = TOTAL_VACATION_DAYS - MIN_VACATION_DURATION
        if old_vac_duration.days > max_remainder:
            return "Usuário já utilizou todas as férias este ano este ano"

        if not old_vacation.is_sick_leave and old_vac_duration.days < MIN_VACATION_DURATION:
            old_vac_duration = datetime.timedelta(MIN_VACATION_DURATION)

        if old_vac_duration.days + new_vac_duration.days > TOTAL_VACATION_DAYS:
            return "O total de férias ultrapassa o limite"
    
        return 0

    @classmethod
    def check_concomitant_vacations(cls, start_date, end_date, user_id):
        """check if user's vacation requests that overlap with other users vacation requests"""

        no_check = ['pending_approval', 'approved']
        vacs = cls.query.filter(cls.user_id != user_id).filter(~cls.status.in_(no_check)).all()

        print(vacs)


    @classmethod
    def check_vacation_entitlement(cls, user_id, start_date):
        """Check if user has been compliant with the rules for at least 6 months"""
        from app.global_vars import MINIMUM_MONTHS_COMPLIENCE_FOR_VACATION
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return "Usuário não encontrado"

        if user.compliant_since is None:
            return "Usuário não tem direito base à férias"

        diff_years = start_date.year - user.compliant_since.year
        diff_months = start_date.month - user.compliant_since.month
        diff_time = diff_years * 12 + diff_months

        if diff_time < MINIMUM_MONTHS_COMPLIENCE_FOR_VACATION:
            return f"""Não foi atingido o tempo mínimo de 6 meses para férias.
                     O usuário está em conformidade desde {user.compliant_since.strftime('%m/%Y')}"""
        
        return 0
 

# =============================== REPORT METHODS ================================================#
    @classmethod
    def get_report(cls):
        translation_dict = {
            "pending_approval": "Pendente",
            "defered": "Deferido",
            "approved": "Aprovado",
            "denied": "Negado",
            "completed": "Concluído",
            "ongoing": "Em andamento",
            "paid": "Pago",
            "unapproved": "Aprovação Retirada",
            "archived": "Arquivado",
            "deleted": "Apagado",
        }
        
        vacations = cls.query.filter(~cls.status.in_(['deleted'])).order_by(desc(cls.id)).all()
        output = []
        for vacation in vacations:
            output.append({
                "id": vacation.id,
                "name": vacation.user.full_name,
                "crm": vacation.user.crm,
                "type": "Licença Médica" if vacation.is_sick_leave else "Férias",
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


#=============================== UTILITY METHODS ================================================#
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