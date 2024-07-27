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
#     aug = Month.query.filter_by(number=8, year=2024).first()
#     print(len(aug.users))
#     sept = Month.query.filter_by(number=9, year=2024).first()
#     print(len(sept.users))
#     oct = Month.query.filter_by(number=10, year=2024).first()
#     print(len(oct.users))    