import migration_funcs
from app.models import User, Center, Month
from app import create_app, db
from app.models._funcs import unify_appointments


# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.migrate_base("CCQ--BASE")

app = create_app()
with app.app_context():
    # month = Month.create_new_month(number=12, year=2023)
    # month = Month.query.filter_by(number=12, year=2023).first()
    # month.set_current()
    # month.populate()
    # month.gen_appointments()
    # month.unlock()
    pass