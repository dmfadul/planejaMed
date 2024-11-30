# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message, BaseAppointment, Vacation
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict
from app.config import Config
import app.hours_conversion as hc
from datetime import datetime
import json


app = create_app()
with app.app_context():
    crm = 38415
    user = User.query.filter_by(crm=crm).first()
    print(user.full_name)

    v = Month.check_vacation_entitlement(user.id, 9, 2024)
    print(v)


def create_dates_txt():
    app = create_app()
    with app.app_context():
        user_dates = ""
        done_users = []
        # user_dates += "ADMINITRATIVO\n\n"

        users = sorted(User.query.all(), key=lambda x: x.full_name)
        for user in users:
            if not user.is_active or not user.is_visible:
                done_users.append(user.id)
                continue
            
            if user.pre_approved_vacation:
                user_dates += f"{user.full_name}\n"
                done_users.append(user.id)


        user_dates += "\n\nSEM DIREITO BASE\n\n"
        for user in users:
            if user.id in done_users:
                continue

            base_test = Month.check_vacation_entitlement(user.id, 11, 2024)
            if isinstance(base_test, str) and "Base" in base_test:
                user_dates += f"{user.full_name}\n"
                done_users.append(user.id)


        user_dates += "\n\nCUMPREM AS REGRAS HÁ MAIS DE SEIS MESES\n\n"
        for user in users:
            if user.id in done_users:
                continue

            break_flag = False
            for m in range(12, 5, -1):
                v = Month.check_vacation_entitlement(user.id, m, 2024)

                if isinstance(v, str):
                    if ('rotina' in v) or ('plantão' in v):
                        break_flag = True
                        break
                    
            if break_flag:
                continue
            
            done_users.append(user.id)
            user_dates += f"{user.full_name}\n"


        user_dates += "\n\nOUTROS\n\n"
        for user in users:
            if user.id in done_users:
                continue

            break_flag = False
            for m in range(11, 4, -1):
                v = Month.check_vacation_entitlement(user.id, m, 2024)

                if isinstance(v, str):
                    if ('rotina' in v) or ('plantão' in v):
                        break_flag = True
                        date = datetime(2024, m, 26)
                        user_dates += f"{user.full_name:<50} {date.date().strftime('%d/%m/%Y')}\n"
                        break
                    
            if break_flag:
                continue
            
            user_dates += f"{user} - {user.date_joined}\n"

        with open("user_dates.txt", "w") as f:
            f.write(user_dates)


# create_dates_txt()
