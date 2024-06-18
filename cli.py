import migration_funcs
from app.models import User, Center, Month, Appointment, Day
from app import create_app, db
from app.hours_conversion import unify_appointments
from datetime import datetime

# migration_funcs.add_centers()
# migration_funcs.migrate_users()
migration_funcs.migrate_base("CCG--BASE")

app = create_app()
with app.app_context():
    # d = datetime(2023, 11, 27)
    # center = Center.query.filter_by(abbreviation="CCG").first()
    # day = Day.query.filter_by(date=d).first()
    
    # appointments = Appointment.query.filter_by(center_id=center.id, day_id=day.id).all()
    # user = User.query.filter_by(crm="26704").first()
    
    # print(user.filtered_appointments(center.id, day.id))


    # user_1 = User.query.filter_by(crm="26704").first()
    # appointments = [app.hour for app in user_1.appointments if app.day.date.day == 26]
    # print(appointments)

    # user_2 = User.query.filter_by(crm="42173").first()
    # appointments_2 = [app.hour for app in user_2.appointments if app.day.date.day == 5]
    # print(appointments_2)


    # month = Month.create_new_month(number=12, year=2023)
    # month = Month.query.filter_by(number=12, year=2023).first()
    # month.set_current()
    # month.populate()
    # month.gen_appointments()
    # month.unlock()
    pass