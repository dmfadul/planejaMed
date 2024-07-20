import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from datetime import datetime
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict


# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()
# migration_funcs.migrate_base("CCG--BASE")
# migration_funcs.migrate_months()
# migration_funcs.migrate_month("CCG", 12, 2023)


# app = create_app()

# with app.app_context():
#     messages = Message.query.all()
#     print(messages)

    # for message in messages:
    #     message.delete()

#     for app in [app for app in req.appointments if app.user_id == req.requester_id]:
#         print(app.user_id, int(req.receivers_code))
#         # app.change_doctor(int(req.receivers_code))

#     for app in [app for app in req.appointments if app.user_id == int(req.receivers_code)]: 
#         print(app.user_id, req.requester_id)
#         # app.change_doctor(req.requester_id)

    # user = User.query.filter_by(crm=26704).first()
    # month = Month.get_current()
    # day = month.get_day(15)
    # center = Center.query.filter_by(abbreviation="CCG").first()
    
    # appointments = Appointment.query.filter_by(user_id=user.id,
    #                                           day_id=day.id,
    #                                           center_id=center.id).all()
    
    # for app in appointments:
    #     print(app.day.date, app.hour, app.requests)