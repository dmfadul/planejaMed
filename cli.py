import migration_funcs
from app.models import User, Center, Month, Appointment, Day
from app import create_app, db


# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.migrate_base("CCG--BASE")

app = create_app()
with app.app_context():
    # month = Month.create_new_month(12, 2023)
    month = Month.query.filter_by(number=12, year=2023).first()
    month.populate()
    month.gen_appointments()
    pass