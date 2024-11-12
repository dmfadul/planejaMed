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
    user = User.query.filter_by(crm=34085).first()
    print(user)
    user.get_original_appointments_by_month(11, 2024)
#     print(user.get_original_appointments_by_month(12, 2024))
#     user = User.query.filter_by(crm=26704).first()
#     s_date = datetime(2024, 12, 1)
#     e_date = datetime(2024, 12, 30)

#     vacation = Vacation(user_id=user.id,
#                         start_date=s_date,
#                         end_date=e_date)
    
    # print(Vacation.check(user.id))
    # vacation.check()

#     users = User.query.all()
#     for user in users:
#         if user.crm in vacs_crm:
#             print(f"Pre-approving {user}")
#             user.pre_approved_vacation = True
#             db.session.commit()
#         else:
#             print(f"Skipping {user}")
#             user.pre_approved_vacation = False
#             db.session.commit()

  

# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()

# migration_funcs.migrate_base("CCG--BASE")

# migration_funcs.migrate_months()
