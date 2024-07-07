# import migration_funcs
from app.models import User, Center, Month, Appointment, Day
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from datetime import datetime
from app.hours_conversion import appointments_letters_key


# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()
# migration_funcs.migrate_base("CCG--BASE")


# print(convert_hours(["-", "01:00", "18:00"]))

# t = ["m6", "d11", "n"]
# t = sorted(t, key=appointments_letters_key)
# print(t)

# app = create_app()
# with app.app_context():
#     test = User.query.filter_by(crm=26704).first()
#     print(test.app_dict)


    # days = []
    # for app in month.appointments:
    #     days.append(app.day.date)

    # unique = sorted(list(set(days)))

    # for day in unique:
    #     print(day.strftime("%d/%m/%Y"))

    


    # month = Month.query.filter_by(number=12, year=2023).first()
    # month.set_current()
    
    # month = migration_funcs.prepare_month(12, 2023)
    # month.set_current()

# app = create_app()
# with app.app_context():
#     month = Month.query.filter_by(number=1, year=2024).first()
#     month.delete()
    # doctor = User.query.filter_by(crm=42390).first()
    # for app in doctor.appointments:
    #     print(app.day, app.hour)
    # month = Month.create_new_month(12, 2023)
    # month = Month.query.filter_by(number=12, year=2023).first()
    # month.populate()
    # month.gen_appointments()
    # pass