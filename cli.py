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
    # user = User.query.filter_by(crm=42217).first()
    # print(user.full_name)
    # v = Month.check_vacation_entitlement(user.id, 6, 2024)
    # print(v)

    user_dates = ""
    done_users = []
    user_dates += "ADMINITRATIVO\n\n"
    
    users = sorted(User.query.all(), key=lambda x: x.full_name)
    for user in users:
        if not user.is_active or not user.is_visible:
            done_users.append(user.id)
            continue
        
        if user.pre_approved_vacation:
            user_dates += f"{user.abbreviated_name}\n"
            done_users.append(user.id)

    
    user_dates += "\n\nSEM DIREITO BASE\n\n"
    for user in users:
        if user.id in done_users:
            continue

        base_test = Month.check_vacation_entitlement(user.id, 11, 2024)
        if isinstance(base_test, str) and "Base" in base_test:
            user_dates += f"{user.abbreviated_name}\n"
            done_users.append(user.id)

    
    user_dates += "\n\n CUMPREM AS REGRAS HÁ MAIS DE SEIS MESES\n\n"
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
        user_dates += f"{user.abbreviated_name}\n"

    
    user_dates += "\n\nOUTROS\n\n"
    for user in users:
        if user.id in done_users:
            continue

        break_flag = False
        for m in range(12, 5, -1):
            v = Month.check_vacation_entitlement(user.id, m, 2024)

            if isinstance(v, str):
                if ('rotina' in v) or ('plantão' in v):
                    break_flag = True
                    date = datetime(2024, m, 26)
                    user_dates += f"{user.abbreviated_name} \t\t-\t\t {date.date().strftime("%d/%m/%Y")}\n"
                    break
        
        if break_flag:
            continue
        
        user_dates += f"{user} - {user.date_joined}\n"
        
    with open("user_dates.txt", "w") as f:
        f.write(user_dates)


        # if all([v == 0 for v in results.values()]):
        #     # print(f"{user.abbreviated_name} - YES")
        #     continue
        
        # if results.get(11) in ['ROT', 'PLT']:
        #     continue

        
            

    #     base_check = not any([d < 0 for d in BaseAppointment.get_users_delta(user.id).values()])

    #     if not base_check:
    #         user_dates += f"{user.crm}:\t\t 0\t\t\t\t\t - \t\t\t {user.abbreviated_name}\n"
    #         continue

    #     user_dates += f"{user.crm}:\t\t {user.date_joined}\t\t\t - \t\t\t {user.abbreviated_name}\n"
    
    # with open("user_dates.txt", "w") as f:
    #     f.write(user_dates)
