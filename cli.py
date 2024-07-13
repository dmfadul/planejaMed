import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from datetime import datetime
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list, convert_line_to_hour
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
#     user = User.query.filter_by(crm=20000).first()
#     print(user.is_waiting_for_approval)
#     print(user.is_active)