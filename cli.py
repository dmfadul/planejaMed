import migration_funcs
from app.models import User, Center, Month
from app import create_app
from app.models._funcs import unify_appointments


# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.migrate_base("CCQ--BASE")

app = create_app()
with app.app_context():
    month = Month.gen_new_month(12, 2023)
    print(month)
