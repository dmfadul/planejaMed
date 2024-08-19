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


# test_lists = [
#     [0, 1, 2, 3, 4, 5],               # Full "m" period
#     [6, 7, 8, 9, 10, 11],             # Full "t" period
#     [12, 13, 14, 15, 16, 17],         # Full "c" period
#     [18, 19, 20, 21, 22, 23],         # Full "v" period
#     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],   # "m" and partial "t"
#     [12, 13, 14, 15, 16, 17, 18],     # "c" and partial "v"
#     [0, 23],                          # Edge case: Start and end of the day
#     [11, 12, 13],                     # Transition between "t" and "c"
#     [10, 11, 12, 13, 14],             # "t" and partial "c"
#     [6, 7, 8],                        # Partial "t"
#     [18, 19, 20],                     # Partial "v"
#     [0, 1, 22, 23],                   # Edge hours from "m" and "v"
#     [6, 8, 10, 12, 14],               # Non-contiguous hours across "t" and "c"
#     [0, 12, 23],                      # Start, middle, and end of the day
#     [2, 3, 4, 18, 19, 20],            # "m" and partial "v"
#     [0, 1, 2, 21, 22, 23],            # "m" and partial "v" with gap
#     [5, 6, 7, 8, 9, 10, 11, 12, 13],  # Overlapping "m", "t", and "c"
#     [10, 11, 12, 13, 14, 15, 16],     # "t" and partial "c" into "v"
#     [3, 4, 5, 6, 7, 8, 9, 10],        # Late "m" and early "t"
#     [20, 21, 23, 0, 1],           # Night and early morning transition
# ]

# for l in test_lists:
#     print(l)
#     print(hc.gen_redudant_hour_list(l))
#     print(hc.gen_redudant_hour_list(l, include_line=True))
#     print(hc.gen_redudant_hour_list_(l))
#     print(hc.gen_redudant_hour_list_(l, include_line=True))
#     print("\n")

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

