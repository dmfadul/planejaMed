import migration_funcs
from app.models import User, Center, Month, Appointment, Day
from app import create_app, db


migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.migrate_base("CCG--BASE")

app = create_app()
with app.app_context():
    pass