from app import db
from app.models import User, BaseAppointment, Month
import app.global_vars as global_vars


class Vacation(db.Model):
    __tablename__ = "vacations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False, default='pending')

    user = db.relationship('User', back_populates='vacations', lazy=True)
    

    @classmethod
    def add_entry(cls, user_id, start_date, end_date):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"

        check = cls.query.filter_by(user_id=user_id, start_date=start_date, end_date=end_date).first()
        if check:
            return check

        vacation = cls(user_id=user_id, start_date=start_date, end_date=end_date)
        db.session.add(vacation)
        db.session.commit()

        return vacation
    
    def remove_entry(self):
        db.session.delete(self)
        db.session.commit()
        return f"Férias de {self.user.abbreviated_name} removidas"

    @classmethod
    def check(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return f"Usuário com id {user_id} não encontrado"

        base_dict = BaseAppointment.get_users_total(user.id, split_the_fifth=True)
        rules_dict = user.get_vacation_rules()

        if base_dict['routine'] < rules_dict['routine'] or base_dict['plaintemps'] < rules_dict['plaintemps']:
            return f"Usuário {user.abbreviated_name} não tem horas suficientes para férias"

        return "Usuário está apto para férias"

    def calculate_payment(self):
        from app.hours_conversion import convert_hours_to_line, sum_hours
        months = self.months_in_range
        
        output = ""
        for year_month in months:
            month = Month.query.filter_by(number=year_month[1], year=year_month[0]).first()
            if not month:
                return "Month not found", 404
        
            original_dict = month.get_original_dict()
            if isinstance(original_dict, str):
                output += original_dict
                continue
            
            doctors_dict = original_dict.get('data').get(str(self.user.crm))

            if not doctors_dict:
                output += f"O médico {doctor.full_name} não tem horas no original do mês {month[1]}/{month[0]}\n"
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

    @property
    def months_in_range(self):
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