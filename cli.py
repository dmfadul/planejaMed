# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from datetime import datetime
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict
from app.config import Config
import app.hours_conversion as hc


t = [7, 8, 9,10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
# r = hc.gen_hour_range((7, 7))
# print(hc.prepare_appointments(t))
# print(hc.gen_redudant_hour_list(t, include_line=True))

print(hc.gen_redudant_hour_list(t))
print(hc.gen_redudant_hour_list(t, include_line=True))
print(hc.gen_redudant_hour_list_(t))
print(hc.gen_redudant_hour_list_(t, include_line=True))


# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()

# migration_funcs.migrate_base("CCG--BASE")

# migration_funcs.migrate_months()

# app = create_app()

# with app.app_context():
#     date = datetime(2024, 8, 16)
#     day = Day.query.filter_by(date=date).first()
#     user = User.query.filter_by(crm=43645).first()
    
#     appointments = Appointment.query.filter_by(user_id=user.id, day_id=day.id).all()
#     for app in appointments:
#         print(app.center.abbreviation, app.hour)

# config = Config()

# print(config.get('maintenance_mode'))

