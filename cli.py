# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from datetime import datetime
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list, convert_line_to_hour
from app.routes.calendar.gen_data import gen_days_dict


# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()
# migration_funcs.migrate_base("CCG--BASE")

# print(convert_line_to_hour("n11: 19:00 - 06:00"))

# hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
# print(gen_redudant_hour_list(hours, include_line=True))

# app = create_app()

# with app.app_context():  
#     requests = Request.query.all()
#     for request in requests:
#         request.delete()