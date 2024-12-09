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


# app = create_app()
# with app.app_context():
#     user = User.query.filter_by(crm=44392).first()
#     print(user.vacations)
#     print(Month.check_vacation_entitlement(user.id, 12, 2024))
#     print(Month.get_vacation_entitlement_report(user.id, 12, 2024))

    # month = Month.get_current()
    # user = User.query.filter_by(crm=26704).first()
    # print(month.check_vacation_entitlement(user.id, month.number, month.year))

    # month = Month.get_current()
    # o = Month.check_for_vacation_entitlement_loss(month.number, month.year)
    # print(o)

    # crm = 40506
    # user = User.query.filter_by(crm=crm).first()
    # print(user.full_name)

    # start_date = datetime(2024, 11, 26)
    # Vacation.check_vacation_entitlement(user.id, start_date)

    # v = Month.get_vacation_entitlement_report(user.id, 11, 2024)
    # print(v)


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


# def populate_compliance():
#     app = create_app()
#     with app.app_context():
#         users = sorted(User.query.all(), key=lambda x: x.full_name)
#         for user in users:
#             if not user.is_active or not user.is_visible:
#                 continue
            
#             if user.pre_approved_vacation:
#                 print(user.full_name, "admin")
#                 user.compliant_since = user.date_joined
#                 user.compliance_history = user.date_joined
#                 db.session.commit()
#                 continue

#             base_test = Month.check_vacation_entitlement(user.id, 11, 2024)
#             if isinstance(base_test, str) and "Base" in base_test:
#                 print(user.full_name, "Sem Base")
#                 continue

#             break_flag = False
#             for m in range(11, 4, -1):
#                 v = Month.check_vacation_entitlement(user.id, m, 2024)

#                 if isinstance(v, str):
#                     if ('rotina' in v) or ('plantão' in v):
#                         break_flag = True
#                         print(user.full_name, f"{datetime(2024, m, 26).date().strftime('%d/%m/%Y')}")
#                         user.compliant_since = datetime(2024, m, 26)
#                         user.compliance_history = datetime(2024, m, 26)
#                         db.session.commit()
#                         break
                    
#             if break_flag:
#                 continue
            
#             print(user.full_name, "6 meses")
#             user.compliant_since = user.date_joined
#             user.compliance_history = user.date_joined
#             db.session.commit()
#             continue

