# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message, BaseAppointment, Vacation
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict
import app.hours_conversion as hc
from app.config import Config
from datetime import datetime
from timeit import timeit
import json


app = create_app()
with app.app_context():
    user = User.query.filter_by(first_name="Victor").first()
    print(user)
    # user.lose_vacation_entitlement()
    user.recover_vacation_rights()
    # user.gain_vacation_entitlement()

# user_id = 34
# center_id = 1

# app = create_app()
# with app.app_context():
#     user = User.query.filter_by(id=user_id).first()

#     for day_id in range(300, 397):
#         # Define a wrapper for the filtered_appointments method
#         def test_filtered_appointments():
#             return user.filtered_appointments(center_id=center_id, day_id=day_id, unified=False)

#         # Define a wrapper for the filtered_appointments_ method
#         def test_filtered_appointments_():
#             return user.filtered_appointments_(center_id=center_id, day_id=day_id, unified=False)

#         # Run timeit for both methods
#         time_filtered_appointments = timeit(test_filtered_appointments, number=1000)
#         time_filtered_appointments_ = timeit(test_filtered_appointments_, number=1000)

#         print(f"Time for filtered_appointments: {time_filtered_appointments} seconds")
#         print(f"Time for filtered_appointments_: {time_filtered_appointments_} seconds")

#         app = test_filtered_appointments()
#         app_ = test_filtered_appointments_()

#         print(app == app_)


# app = create_app()
# with app.app_context():
#     print(Month.get_actual_date(26, 12, 2024))
#     user = User.query.filter_by(crm=40022).first()
#     print(user.full_name)
#     print(Month.get_vacation_entitlement_report(user.id, 10, 2024))
#     print(Month.get_vacation_entitlement_balance(user.id, 10, 2024))

    # leo = User.query.filter_by(crm=42586).first()
    # renato = User.query.filter_by(crm=31342).first()

    # reqs = Request.query.all()
    # for r in renato.requests_received:
    #     if '09/12/24' in r.info or '23/12/24' in r.info:
    #         reqs.append(r)

    # for r in leo.requests_received:
    #     if '09/12/24' in r.info or '23/12/24' in r.info:
    #         reqs.append(r)

    # for r in renato.requests_sent:
    #     if '09/12/24' in r.info or '23/12/24' in r.info:
    #         reqs.append(r)
            
    # for r in leo.requests_sent:
    #     if '09/12/24' in r.info or '23/12/24' in r.info:
    #         reqs.append(r)


    # reqs = list(set(reqs))
    # reqs = [r for r in reqs if '09/12/24' in r.info or '23/12/24' in r.info]
    # reqs = sorted(reqs, key=lambda x: x.creation_date)


    # for r in reqs:
    #     print(r.creation_date, r.info, r.response, r.response_date)

    # req1 = Request.query.filter_by(id=556).first()
    # req2 = Request.query.filter_by(id=561).first()

    # print(req1)
    # for a in req1.appointments:
    #     print(a, a.center.abbreviation, a.day, a.hour, a.user)
    # print('---'*10)
    # print(req2)
    # for a in req2.appointments:
    #     print(a, a.center.abbreviation, a.day, a.hour, a.user)

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


# def create_dates_txt():
#     app = create_app()
#     with app.app_context():
#         user_dates = ""
#         done_users = []
#         # user_dates += "ADMINITRATIVO\n\n"

#         users = sorted(User.query.all(), key=lambda x: x.full_name)
#         for user in users:
#             if not user.is_active or not user.is_visible:
#                 done_users.append(user.id)
#                 continue
            
#             if user.pre_approved_vacation:
#                 user_dates += f"{user.full_name}\n"
#                 done_users.append(user.id)


#         user_dates += "\n\nSEM DIREITO BASE\n\n"
#         for user in users:
#             if user.id in done_users:
#                 continue

#             base_test = Month.check_vacation_entitlement(user.id, 11, 2024)
#             if isinstance(base_test, str) and "Base" in base_test:
#                 user_dates += f"{user.full_name}\n"
#                 done_users.append(user.id)


#         user_dates += "\n\nCUMPREM AS REGRAS HÁ MAIS DE SEIS MESES\n\n"
#         for user in users:
#             if user.id in done_users:
#                 continue

#             break_flag = False
#             for m in range(12, 5, -1):
#                 v = Month.check_vacation_entitlement(user.id, m, 2024)

#                 if isinstance(v, str):
#                     if ('rotina' in v) or ('plantão' in v):
#                         break_flag = True
#                         break
                    
#             if break_flag:
#                 continue
            
#             done_users.append(user.id)
#             user_dates += f"{user.full_name}\n"


#         user_dates += "\n\nOUTROS\n\n"
#         for user in users:
#             if user.id in done_users:
#                 continue

#             break_flag = False
#             for m in range(11, 4, -1):
#                 v = Month.check_vacation_entitlement(user.id, m, 2024)

#                 if isinstance(v, str):
#                     if ('rotina' in v) or ('plantão' in v):
#                         break_flag = True
#                         date = datetime(2024, m, 26)
#                         user_dates += f"{user.full_name:<50} {date.date().strftime('%d/%m/%Y')}\n"
#                         break
                    
#             if break_flag:
#                 continue
            
#             user_dates += f"{user} - {user.date_joined}\n"

#         with open("user_dates.txt", "w") as f:
#             f.write(user_dates)


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

