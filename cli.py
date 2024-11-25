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
    user = User.query.filter_by(crm=42210).first()
    print(user.full_name)
    v = Vacation.check_vacation_entitlement(user.id, 5, 2024)
    print(v)

    # user_dates = ""
    # users = sorted(User.query.all(), key=lambda x: x.full_name)
    # for user in users:
    #     if not user.is_active or not user.is_visible:
    #         continue
        
    #     base_check = not any([d < 0 for d in BaseAppointment.get_users_delta(user.id).values()])

    #     if not base_check:
    #         user_dates += f"{user.crm}:\t\t 0\t\t\t\t\t - \t\t\t {user.abbreviated_name}\n"
    #         continue

    #     user_dates += f"{user.crm}:\t\t {user.date_joined}\t\t\t - \t\t\t {user.abbreviated_name}\n"
    
    # # with open("user_dates.txt", "w") as f:
    # #     f.write(user_dates)

    #     results = {}
    #     for m in range(1, 11):
    #         v = Vacation.check_vacation_entitlement(user.id, m, 2024)

    #         if isinstance(v, str):
    #             if 'rotina' in v:
    #                 results[m] = 'ROT'
    #             elif 'plantão' in v:
    #                 results[m] = 'PLT'
    #             else:
    #                 results[m] = v
    #         else:
    #             results[m] = v

    #     if all([v == 0 for v in results.values()]):
    #         # print(f"{user.abbreviated_name} - YES")
    #         continue
        
    #     if results.get(11) in ['ROT', 'PLT']:
    #         continue

    #     print(f"{user.abbreviated_name} - {results}")
        
            


    # Vacation.check_concomitant_vacations("2024-11-20", "2024-11-26", user.id)
    
    # datetime_object = datetime.strptime("2024-11-20", "%Y-%m-%d")
    # Vacation.check(datetime_object, 26)
